// 🔍 DETAIL MODAL (Material Code)
const materialModal = document.getElementById('detailModal');
let previouslySelectedRow = null;

materialModal.addEventListener('show.bs.modal', function (event) {
  const link = event.relatedTarget;

  document.getElementById("modalMaterialCode").textContent = link.getAttribute("data-material_code");
  document.getElementById("modalEquipmentName").textContent = link.getAttribute("data-equipment_name");
  document.getElementById("modalMaterialDescription").textContent = link.getAttribute("data-material_description");
  document.getElementById("modalPartNo").textContent = link.getAttribute("data-part_no");
  document.getElementById("modalAssembly").textContent = link.getAttribute("data-assembly");
  document.getElementById("modalPosNo").textContent = link.getAttribute("data-pos_no");
  document.getElementById("modalInstalledQty").textContent = link.getAttribute("data-installed_qty");
  document.getElementById("modalRemark").textContent = link.getAttribute("data-remark");

  // Row highlight effect
  const row = link.closest("tr");
  if (previouslySelectedRow) previouslySelectedRow.classList.remove("selected-row");
  row.classList.add("selected-row");
  previouslySelectedRow = row;
});

// 🧾 PR MODAL (Purchase Requisition)
const prModal = document.getElementById('prModal');

prModal.addEventListener('show.bs.modal', function (event) {
  const link = event.relatedTarget;

  document.getElementById("modalPrNumber").textContent = link.getAttribute("data-pr_number");
  document.getElementById("modalPrQty").textContent = link.getAttribute("data-quantity");
  document.getElementById("modalPrDate").textContent = link.getAttribute("data-date");
});

// 📦 PO MODAL (Purchase Order)
const poModal = document.getElementById('poModal');

poModal.addEventListener('show.bs.modal', function (event) {
  const link = event.relatedTarget;

  document.getElementById("modalPoNumber").textContent = link.getAttribute("data-po_number");
  document.getElementById("modalPoQty").textContent = link.getAttribute("data-quantity");
  document.getElementById("modalPoDate").textContent = link.getAttribute("data-date");
  document.getElementById("modalPoVendor").textContent = link.getAttribute("data-vendor");
});
