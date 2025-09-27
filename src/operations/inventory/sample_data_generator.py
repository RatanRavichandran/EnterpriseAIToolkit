import pandas as pd

# Stock Levels Data
stock_levels = pd.DataFrame({
    'ProductID': [1001, 1002, 1003, 1004, 1005],
    'ProductName': ['Organic Apples', 'Whole Wheat Bread', 'Almond Milk', 'Chicken Breasts', 'Fresh Tomatoes'],
    'CurrentStock': [150, 50, 80, 200, 70],
    'ReorderPoint': [100, 30, 60, 150, 50],
    'SupplierID': ['S001', 'S002', 'S003', 'S004', 'S001']
})
stock_levels.to_csv('stock_levels.csv', index=False)

# Inventory Turnover Rates Data
inventory_turnover = pd.DataFrame({
    'ProductID': [1001, 1002, 1003, 1004, 1005],
    'ProductName': ['Organic Apples', 'Whole Wheat Bread', 'Almond Milk', 'Chicken Breasts', 'Fresh Tomatoes'],
    'TurnoverRate': [5.2, 3.1, 4.8, 2.7, 3.6],
    'LastMonthSales': [520, 310, 384, 540, 252],
    'LastMonthStock': [100, 50, 80, 200, 70]
})
inventory_turnover.to_csv('inventory_turnover.csv', index=False)

# Supplier Performance Data
supplier_performance = pd.DataFrame({
    'SupplierID': ['S001', 'S002', 'S003', 'S004'],
    'SupplierName': ['Fresh Fruits Co', 'Bakery Supplies', 'Nutty Goods Inc', 'Poultry Pro Ltd'],
    'OnTimeDeliveryRate': ['95%', '89%', '92%', '85%'],
    'AverageLeadTime (Days)': [5, 7, 6, 8],
    'QualityScore': [8.5, 7.8, 9.2, 7.5]
})
supplier_performance.to_csv('supplier_performance.csv', index=False)

# Stock Replenishment Data
stock_replenishment = pd.DataFrame({
    'ProductID': [1001, 1002, 1003, 1004, 1005],
    'ProductName': ['Organic Apples', 'Whole Wheat Bread', 'Almond Milk', 'Chicken Breasts', 'Fresh Tomatoes'],
    'RequiredStock': [200, 100, 120, 250, 120],
    'CurrentStock': [150, 50, 80, 200, 70],
    'ReorderQuantity': [100, 80, 50, 100, 70],
    'SupplierID': ['S001', 'S002', 'S003', 'S004', 'S001']
})
stock_replenishment.to_csv('stock_replenishment.csv', index=False)

# Supply Chain Metrics Data
supply_chain_metrics = pd.DataFrame({
    'MetricID': ['M001', 'M002', 'M003', 'M004', 'M005'],
    'MetricName': ['AverageOrderCycleTime', 'OrderFulfillmentRate', 'InventoryCarryingCost', 'StockoutFrequency', 'SupplierReliability'],
    'Value': ['12 days', '90%', '$5000', '3 times/month', '88%']
})
supply_chain_metrics.to_csv('supply_chain_metrics.csv', index=False)
