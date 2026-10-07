from suppliers.models import SupplierProduct
from procurement.models import PurchaseOrder, PurchaseOrderItem



def select_suppliers(purchase_request):
    """
    Select suppliers for all products in an approved Purchase Request.
    """

    requested_items = purchase_request.items.select_related("product").all()

    requested_quantities = {
        item.product_id: item.quantity
        for item in requested_items
    }

    supplier_options = {}

    for product_id, quantity in requested_quantities.items():
        options = SupplierProduct.objects.filter(
            product_id=product_id,
            is_active=True
        ).select_related("supplier", "product")

        supplier_options[product_id] = options

    for product_id, options in supplier_options.items():
        if not options.exists():
            raise ValueError(
                f"No active supplier found for product ID {product_id}."
            )

    all_product_ids = set(requested_quantities.keys())

    supplier_product_map = {}

    for product_id, options in supplier_options.items():
        for option in options:
            supplier_id = option.supplier_id

            if supplier_id not in supplier_product_map:
                supplier_product_map[supplier_id] = set()

            supplier_product_map[supplier_id].add(product_id)

    complete_suppliers = [
        supplier_id
        for supplier_id, product_ids in supplier_product_map.items()
        if product_ids == all_product_ids
    ]

    if complete_suppliers:
        supplier_scores = []

        for supplier_id in complete_suppliers:
            supplier_products = SupplierProduct.objects.filter(
                supplier_id=supplier_id,
                product_id__in=all_product_ids,
                is_active=True
            )

            total_cost = 0
            max_lead_time = 0

            for supplier_product in supplier_products:
                quantity = requested_quantities[supplier_product.product_id]

                total_cost += (
                    supplier_product.purchase_price * quantity
                )

                max_lead_time = max(
                    max_lead_time,
                    supplier_product.lead_time_days
                )

            supplier_scores.append(
                (
                    total_cost,
                    max_lead_time,
                    supplier_id
                )
            )

        supplier_scores.sort()

        best_supplier_id = supplier_scores[0][2]

        print("Selected supplier:", best_supplier_id)


    selected_suppliers = {}

    if complete_suppliers:
        for product_id in all_product_ids:
            selected_suppliers[product_id] = best_supplier_id

    else:
        for product_id, options in supplier_options.items():
            best_option = min(
                options,
                key=lambda option: (
                    option.purchase_price,
                    option.lead_time_days,
                    option.supplier_id
                )
            )

            selected_suppliers[product_id] = best_option.supplier_id

    return {
    SupplierProduct.objects.get(
        product_id=product_id,
        supplier_id=supplier_id
    ).product.product_code: SupplierProduct.objects.get(
        product_id=product_id,
        supplier_id=supplier_id
    ).supplier.supplier_id
    for product_id, supplier_id in selected_suppliers.items()
}


def create_purchase_order(purchase_request):
    """
    Create a Purchase Order automatically for an approved Purchase Request.
    """

    if purchase_request.status != "APPROVED":
        raise ValueError(
            "Purchase Order can only be created for an approved Purchase Request."
        )

    selected_suppliers = select_suppliers(purchase_request)

    last_po = PurchaseOrder.objects.order_by("-id").first()

    if last_po:
        last_number = int(last_po.po_number.split("-")[1])
        next_number = last_number + 1
    else:
        next_number = 1

    po_number = f"PO-{next_number:03d}"

    purchase_order = PurchaseOrder.objects.create(
        po_number=po_number,
        purchase_request=purchase_request,
        status="DRAFT"
    )

    requested_items = purchase_request.items.select_related("product").all()

    for item in requested_items:
        supplier_id = selected_suppliers[item.product.product_code]

        supplier_product = SupplierProduct.objects.get(
            supplier__supplier_id=supplier_id,
            product_id=item.product_id,
            is_active=True
        )

        PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            supplier=supplier_product.supplier,
            product=item.product,
            ordered_quantity=item.quantity,
            received_quantity=0
        )
    return purchase_order




    print("Requested quantities:", requested_quantities)
    

