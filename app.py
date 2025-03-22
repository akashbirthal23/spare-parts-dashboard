import os
from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/")
def index():
    # Query parameters
    page = int(request.args.get("page", 1))
    per_page = 10
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "equipment_name")
    order = request.args.get("order", "asc").lower()

    valid_sort_fields = ["equipment_name", "material_code", "material_description", "part_no", "assembly"]
    sort = sort if sort in valid_sort_fields else "equipment_name"
    order = "desc" if order == "desc" else "asc"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search filters
    where_clause = ""
    params = []

    if search:
        where_clause = """ WHERE 
            equipment_name LIKE %s OR
            material_code LIKE %s OR
            material_description LIKE %s OR
            part_no LIKE %s OR
            assembly LIKE %s
        """
        search_term = f"%{search}%"
        params = [search_term] * 5

    offset = (page - 1) * per_page

    # Main spareparts query
    query = f"""
        SELECT * FROM spareparts
        {where_clause}
        ORDER BY {sort} {order}
        LIMIT %s OFFSET %s
    """
    full_params = params + [per_page, offset]
    cursor.execute(query, full_params)
    rows = cursor.fetchall()

    # Get material codes
    material_codes = [row["material_code"] for row in rows]

    # 🔹 SAP Stock Mapping
    sap_stock_map = {}
    if material_codes:
        placeholders = ','.join(['%s'] * len(material_codes))
        stock_query = f"SELECT material_code, unrestricted_stock FROM sapstock WHERE material_code IN ({placeholders})"
        cursor.execute(stock_query, material_codes)
        for stock_row in cursor.fetchall():
            sap_stock_map[stock_row["material_code"]] = stock_row["unrestricted_stock"]

    # 🔸 PR Mapping
    pr_map = {}
    if material_codes:
        placeholders = ','.join(['%s'] * len(material_codes))
        pr_query = f"""
            SELECT material_code, pr_number, pr_date, quantity_requested
            FROM purchaserequisition
            WHERE material_code IN ({placeholders})
            ORDER BY pr_date DESC
        """
        cursor.execute(pr_query, material_codes)
        for pr in cursor.fetchall():
            code = pr["material_code"]
            if code not in pr_map:
                pr_map[code] = []
            pr_map[code].append(pr)
    pr_filter = request.args.get("pr_filter", "1y")  # Default to last 1 year
    # Filter PRs by 1 year if needed
    filtered_pr_map = {}
    if pr_filter == "all":
        filtered_pr_map = pr_map
    else:
        one_year_ago = date.today() - timedelta(days=365)
        for code, pr_list in pr_map.items():
            filtered_pr_map[code] = [
                pr for pr in pr_list if pr["pr_date"] and pr["pr_date"] >= one_year_ago
            ]    
                
    # 🔸 PO Mapping
    po_map = {}
    if material_codes:
        placeholders = ','.join(['%s'] * len(material_codes))
        po_query = f"""
            SELECT material_code, po_number, order_quantity, po_release_date, vendor_name
            FROM purchaseorder
            WHERE material_code IN ({placeholders})
            ORDER BY po_release_date DESC
        """
        cursor.execute(po_query, material_codes)
        for po in cursor.fetchall():
            code = po["material_code"]
            if code not in po_map:
                po_map[code] = []
            po_map[code].append(po)
            
    # Define 1-year cutoff date
    one_year_ago = date.today() - timedelta(days=365)
    po_filter = request.args.get("po_filter", "1y")  # default: 1 year

    # Filter PO entries per material_code
    filtered_po_map = {}
    if po_filter == "all":
        filtered_po_map = po_map
    else:
        one_year_ago = date.today() - timedelta(days=365)
        for code, po_list in po_map.items():
            filtered_po_map[code] = [
                po for po in po_list if po["po_release_date"] and po["po_release_date"] >= one_year_ago
            ]

        
        
    # Merge SAP + PR into rows
    for row in rows:
        row["sap_stock"] = sap_stock_map.get(row["material_code"], 0)
        row["prs"] = filtered_pr_map.get(row["material_code"], [])
        row["pos"] = filtered_po_map.get(row["material_code"], [])


    # Count total rows
    count_query = f"SELECT COUNT(*) as total FROM spareparts {where_clause}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()["total"]
    total_pages = (total + per_page - 1) // per_page

    cursor.close()
    conn.close()

    return render_template(
    "index.html",
    rows=rows,
    page=page,
    total_pages=total_pages,
    search=search,
    sort=sort,
    order=order,
    po_filter=po_filter,
    pr_filter=pr_filter
    )



if __name__ == "__main__":
    app.run(debug=True)
