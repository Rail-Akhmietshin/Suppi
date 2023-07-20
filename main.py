import json
import pandas as pd
import os
import time

'''
    По умолчанию стоят паузы вывода на 20 секунд. 
    
    Вывод данных на строках: 38, 76, 107, 160, 170, 189
    
'''

path = os.path.join(os.getcwd(), "data.json")

with open(path, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame.from_dict(data)



def get_cost_deliveries() -> dict:
    '''Задача 1. Тариф стоимости доставки для каждого склада'''
    cost_deliveries = {}
    for _, row in df.iterrows():
        warehouse_name = row["warehouse_name"]
        products = row["products"]

        if not cost_deliveries.get(warehouse_name):
            products_quantuty = sum(map(lambda x: x.get("quantity"), products))  # сумма количества товаров в заказе
            cost_deliveries[warehouse_name] = round(abs(row["highway_cost"] / products_quantuty))
    return cost_deliveries


cost_deliveries = get_cost_deliveries()

cs = pd.DataFrame(cost_deliveries, index=["Тариф доставки, стоимость/единица товара"])

time.sleep(20)
print(cs)


def get_info_of_products() -> dict:
    '''Задача 2. Суммарные количество, доход, расход и прибыль для каждого товара'''
    product_data = {}
    for _, row in df.iterrows():
        warehouse_name = row["warehouse_name"]
        cost_delivery = cost_deliveries[warehouse_name]  # тарифы из 1го задания
        products = row["products"]

        for product in products:
            product_name = product["product"]
            old_product = product_data.get(product_name, {})  # сведения о товаре, если товар был однажды загружен

            quantity = product["quantity"]
            price = product["price"]

            income = old_product.get("income", 0) + (quantity * price)
            expenditure = old_product.get("expenditure", 0) + (quantity * cost_delivery)
            profit = income - expenditure

            product_data[product_name] = {
                "quantity": old_product.get("quantity", 0) + quantity,
                "income": income,
                "expenditure": expenditure,
                "profit": profit,
            }
    return product_data


products_info = get_info_of_products()

cs2 = pd.DataFrame(products_info).T
cs2.columns = ["Количество товара", "Доход", "Расход", "Прибыль"]

time.sleep(20)
print(cs2)


def get_profit_with_orders():
    '''Задача 3. Id-заказа, прибыль полученная с заказа и средняя прибыль заказов'''

    order_data = {}
    for _, row in df.iterrows():
        order_id = row["order_id"]
        highway_cost = row["highway_cost"]
        products = row["products"]

        income = 0
        for product in products:
            quantity = product["quantity"]
            price = product["price"]

            income += quantity * price
        profit = income + highway_cost  # так как highway_cost всегда отрицательный

        order_data[f"Заказ {order_id}"] = profit
    return order_data


order_data = get_profit_with_orders()

cs3 = pd.DataFrame(order_data, index=["Прибыль"]).T

cs3.loc["Среднее значение прибыли"] = cs3["Прибыль"].mean()

time.sleep(20)
print(cs3)


def get_procent_profit_with_warehouse():
    '''Задача 4. Процент прибыли продукта заказанного из определенного склада к прибыли этого склада'''
    warehouses_and_products_data = []

    for _, row in df.iterrows():
        warehouse_name = row["warehouse_name"]
        cost_delivery = cost_deliveries[warehouse_name]  # тарифы из 1го задания
        products = row["products"]

        for product in products:
            product_name = product["product"]
            quantity = product["quantity"]
            price = product["price"]

            income = quantity * price
            expenditure = quantity * cost_delivery
            profit = income - expenditure

            for warehouse_with_product in warehouses_and_products_data:
                if warehouse_with_product.get("warehouse_name") == warehouse_name \
                        and warehouse_with_product.get("product_name") == product_name:
                    '''Сведения о товаре, если товар был однажды загружен'''
                    current_product_profit = warehouse_with_product.get("profit", 0)
                    current_product_quantity = warehouse_with_product.get("quantity", 0)

                    warehouse_with_product.update({
                        "profit": profit + current_product_profit,
                        "quantity": quantity + current_product_quantity,
                    })
                    break
            else:
                warehouses_and_products_data.append({
                    "warehouse_name": warehouse_name,
                    "product_name": product_name,
                    "profit": profit,
                    "quantity": quantity,
                })
    return warehouses_and_products_data


procent_profit_with_warehouse = get_procent_profit_with_warehouse()

df = pd.DataFrame(procent_profit_with_warehouse)

df2 = df.sort_values(by=['warehouse_name'])
total_profit_by_warehouse = df2.groupby('warehouse_name')['profit'].transform('sum')

df2['percent_profit_product_of_warehouse'] = (df2["profit"] / total_profit_by_warehouse) * 100

time.sleep(20)
print(df2.to_string())

'''5 задание'''

df3 = df2.sort_values(by=['percent_profit_product_of_warehouse'], ascending=False)
df3['accumulated_percent_profit_product_of_warehouse'] = df3.groupby(
    'warehouse_name'
)['percent_profit_product_of_warehouse'].cumsum()

time.sleep(20)
print(df3.to_string())

'''6 задание'''

df4 = df3.sort_values(by=['accumulated_percent_profit_product_of_warehouse'])


def percent_profit_category(percent: float):
    if percent <= 70:
        return "A"
    elif percent <= 90:
        return "B"
    else:
        return "C"


df4["category"] = df4['accumulated_percent_profit_product_of_warehouse'].map(percent_profit_category)

time.sleep(20)
print(df4.to_string())
