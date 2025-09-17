from vschallan.vschallan import VATSmartChallan


def create_vat_invoice(doc, method=None):
	vschallan = VATSmartChallan()
	vschallan.create_vat_invoice(doc)
