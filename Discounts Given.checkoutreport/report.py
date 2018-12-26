from api.reports import ExportStringType, ExportNumericType, ExportCurrencyType, ExportDateTimeType
from api.reports import Database, Invoice, and_, timedelta

name = 'Discounts Given'
version = '2.0'
description = 'Test 123'
icon = 'icon.png'
isExportable = True
dateSelection = True

localizeHeader = True
exportColumnTypes = [ExportStringType, ExportStringType, ExportStringType, ExportStringType,
                     ExportStringType, ExportDateTimeType, ExportStringType, ExportStringType,
                     ExportNumericType, ExportCurrencyType, ExportCurrencyType, ExportCurrencyType,
                     ExportCurrencyType]
exportColumnWidths = [50, 50, 60, 35, 50, 60, 60, 60, 50, 60, 60, 60, 60]


def data(dateRange):
    productLines = Database.query(Invoice).filter(and_(
        Invoice.date >= dateRange['begin'],
        Invoice.date <= dateRange['end'] + timedelta(days=1),
        Invoice.id_parent != None)).order_by(Invoice.id.desc()).all()  # noqa: E711

    productToLineDict = {}
    for pLine in productLines:

        if hasattr(pLine, 'listPriceEx'):
            listPrice = pLine.listPriceEx
        else:
            listPrice = pLine.i.getPriceex(pLine.metanumberstate)

        if pLine.totalDiscountEx() != 0:
            theProduct = pLine.i
            if theProduct not in productToLineDict:
                productToLineDict[theProduct] = []

            pLineDict = {
                'listPriceEx': listPrice,
                'basePriceEx': pLine.basePriceEx,
                'effectivePriceEx': pLine.priceEx,
                'discount': pLine.totalDiscountEx(),
                'percentage': pLine.discount_percentage,
                'formattedNumber': pLine.parent.formattedNumber(),
                'invoiceDate': pLine.parent.date,
                'employeeName': pLine.parent.employee.name(),
                'customerName': pLine.parent.formattedName(),
                'quantity': pLine.quantity,
                'productCode': pLine.md['code'],
                'productName': pLine.md['name'],
            }

            productToLineDict[theProduct].append(pLineDict)

        else:
            # don't even add to list
            pass

    return {'productToLineDict': productToLineDict, 'products': sorted(productToLineDict.keys())}

    # return {'products': Database.query(Product).filter(Product.deleted==False).all()}


def fast_export_rows(exportData):
    rows = [[u'Code', u'Name', u'Invoice', u'Date', u'Employee',
             u'Customer', u'Quantity', u'List Price', u'Inv Price', u'Disc %', u'Disc Amt']]

    keys = ('productCode', 'productName', 'formattedNumber', 'invoiceDate',
            'employeeName', 'customerName', 'quantity', 'listPriceEx',
            'effectivePriceEx', 'percentage', 'discount')

    productToLineDict = exportData['productToLineDict']
    for product in exportData['products']:
        for row in productToLineDict[product]:
            rows.append([row[k] for k in keys])

    return rows


def exportRows(date_range):

    return fast_export_rows(data(date_range))
