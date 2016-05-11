import os
import sys
from subprocess import Popen, PIPE
import json

MyStores = []
threshold = 5


class Product:
    def __init__(self,id,qty):
        self.id = id
        self.qty = qty

class Store:
    def __init__(self,id):
        self.id = id
        self.products = []
        self.salesfrequency = 0

    def AddProduct(self,id,qty):
        self.products.append(Product(id,qty))



def AddProductToMyStores(storeid,productid,qty):
    for store in MyStores:
        if(store.id == storeid):
            store.AddProduct(productid,qty)
            break

def UpdateProductToMyStores(storeid,productid,qty):
    for store in MyStores:
        if(store.id == storeid):
            store.salesfrequency =  store.salesfrequency + 1
            for product in store.products:
                if (product.id == productid):
                    product.qty = product.qty + qty
    return product.qty

def EmitTopTwoSellingStores():
    top1=0
    top2=0
    top1store=0
    top2store=0
    response = []
    for store in MyStores:
        if(top1<store.salesfrequency ):
            top2=top1
            top2store=top1store
            top1=store.salesfrequency
            top1store=store.id
        elif(top2<store.salesfrequency ):
            top2=store.salesfrequency
            top2store=store.id
    response.append({'topsellingstores':[{'storeid':top1store,'salesfrequency':top1},{'storeid': top2store, 'salesfrequency': top2}]})
    print(json.dumps(response))


def DisplayStores():
    #Display the MyStores List
    for store in MyStores:
        print("Store id :"+store.id)

def DisplayProducts(storeid):
    #Display the MyStores List
    for store in MyStores:
        if (store.id == storeid):
            for product in store.products:
                print("Product id: " + str(product.id) + ",qty :" + str(product.qty))


def getScriptPath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

adirScript = getScriptPath()
afileSimulator = os.path.join(adirScript , '..' , 'storeInventoryGenerator/storeInventoryGenerator-assembly-1.0.jar')

cmd="java -jar %s %s" %(afileSimulator ,"-n 160")
proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
#proc = Popen(['java', '-jar', afileSimulator], stdout=PIPE, stderr=PIPE)
for line in iter(proc.stdout.readline,''):
 element = str(line.rstrip(),'utf8')

 if element == '':
     break

 jsonelement = json.loads(element)

 #Add new stores
 if('store' in jsonelement and jsonelement['t'] == 0):
     MyStores.append(Store(jsonelement['store']['id']))

 #Add initial product quantity
 if ('inventory' in jsonelement and jsonelement['t'] == 0):
     AddProductToMyStores(jsonelement['inventory']['store']['id'],jsonelement['inventory']['product']['id'],jsonelement['inventory']['quantityChange'])

 if(jsonelement['t'] > 0):
     updatedqty = UpdateProductToMyStores(jsonelement['inventory']['store']['id'],jsonelement['inventory']['product']['id'],jsonelement['inventory']['quantityChange'])
     jsonelement["inventory"]["netquantity"] = updatedqty
     if updatedqty < threshold:
         jsonelement["alarm"] = "quantity below "+str(threshold) +"!!!!"
         print(jsonelement)
     EmitTopTwoSellingStores()
