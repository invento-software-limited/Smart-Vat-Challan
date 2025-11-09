from vschallan.vschallan import VATSmartChallan


def create_vat_invoice(doc, method=None):
	vschallan = VATSmartChallan()
	if not doc.status == "Return":
		vschallan.create_vat_invoice(doc)
