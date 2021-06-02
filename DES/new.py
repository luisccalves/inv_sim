import numpy as np
import simpy
import matplotlib.pyplot as plt
import matplotlib as mpl

from Runner import runner
np.random.seed(0)
from math import ceil
from functools import partial
import math
import random

def reorder_function_step(days_cnt,reorder_list,periods=2,daysYear=360):
  __temp = days_cnt % daysYear
  assert len(reorder_list) == periods,'Check the reorder_list or periods entered'
  if __temp < 180:
    return  reorder_list[0]
  if __temp >=180:
    return  reorder_list[1]

def reorder_function_exp(days_cnt,a,b):
  return math.exp(-a*days_cnt) * b



rol = partial(reorder_function_exp,a=-.002,b=150)


class InventoryStore:

    def __init__(self,env,name):
        self.name = name
        self.env = env
        self.next = None
    
    def store_supply(self):
        pass

    def store_order(self):
        pass

def generate_leadtime(m,s):
        __leadtime = np.random.normal(m,s,1).item()
        return(__leadtime if __leadtime>=0 else m)

    
        
def generate_demand(m,s) -> float:
        __temp =  np.random.normal(m,s,1).item()
        return(__temp if __temp>=0 else 0)


class Item:
    def __init__(self,name,reorder_level,reorder_qty,demand,std_demand,leadtime,leadtime_std,selling_price,cost_price,demand_func,lead_time_func) -> None:
        self.name = name 
        self.reorder_level = reorder_level
        self.reorder_qty = reorder_qty
        self.demand =demand 
        self.std_demand = std_demand
        self.leadtime = leadtime
        self.leadtime_std = leadtime_std
        self.selling_price = selling_price
        self.cost_price = cost_price
        self.demand_func = demand_func(self.demand,self.std_demand)
        self.lead_time_func = lead_time_func(self.leadtime,self.leadtime_std)
        self.delivery_batches = 1



def generate_interarrival(param):
        return np.random.exponential(param)

def customer_generate_demand(m,s):
        return np.random.normal(m,s,1).item()


    
class Customer:

    def __init__(self,inter_arrival_time,generate_customer):
        self.inter_arrival_time = inter_arrival_time
        self.generate_customer = generate_customer



class Shop(InventoryStore):

    def __init__(self, name,ItemList,env,type_store,customerobject=None):
        super().__init__(name,env)

        self.ItemList = ItemList
        self.env = env
        self.inventory = 50
        self.num_ordered = 0
        self.revenue = 0
        self.next = None
        self.logistic_cost = 10
        self.type = type_store
        self.customerobject = customerobject
        self.costs = 0
        if self.customerobject is not None:
          self.interarrival = self.customerobject.inter_arrival_time(1)
          self.generate_customer = self.customerobject.generate_customer(10,1)
        
    def store_supply(self,demand_child):

      print(f'{self.name} i was called in store supply')
      yield self.env.timeout(1)
      if demand_child < self.inventory:
        self.revenue += self.ItemList.selling_price*demand_child
        self.inventory -= demand_child
        #print(f'customer comes I sold {self.demand} at time {round(self.env.now,2)}')
      else:
          if self.type=='store':
            self.revenue += self.ItemList.selling_price*self.inventory
          self.inventory = 0 
        #print(f'{self.inventory} is out of stock at {round(self.env.now,2)}')
      if self.inventory <= (self.ItemList.reorder_level) and self.num_ordered ==0 and self.type !='warehouse':
        print(f'store reorder is called')
        self.num_ordered = self.ItemList.reorder_qty + 1 -self.inventory
        self.num_ordered = ceil(self.num_ordered/self.ItemList.reorder_qty)*self.ItemList.reorder_qty
        self.env.process(self.store_order(self.num_ordered))
      if self.inventory <= (self.ItemList.reorder_level) and self.num_ordered ==0 and self.type =='warehouse':
        print(f'warehouse reorder is called')
        self.num_ordered = self.ItemList.reorder_qty + 1 -self.inventory
        self.num_ordered = ceil(self.num_ordered/self.ItemList.reorder_qty)*self.ItemList.reorder_qty
        self.env.process(self.warehouse_order())

        

    def store_order(self,num_ordered_qty):
        print(f'{self.name} i was called in store order')
        if num_ordered_qty > self.next.inventory:
          self.next.inventory = 0
        else:
          self.next.inventory -= num_ordered_qty
        self.inventory = num_ordered_qty
        self.num_ordered = 0

        if self.next.inventory <= (self.ItemList.reorder_level) and self.next.num_ordered ==0:
            print(f'store order for next level is called')

            self.env.process(self.next.store_supply(self.next.num_ordered))
        
        yield self.env.timeout(1)
    def warehouse_order(self) -> None:
      print(f'{self.name} i was called in store supply')
      self.num_ordered = self.ItemList.reorder_level + 1 -self.inventory
      self.num_ordered = ceil(self.num_ordered/self.ItemList.reorder_level)*self.ItemList.reorder_qty
      yield self.env.timeout(1)
      self.costs += self.ItemList.cost_price*self.num_ordered + 10 
      for i in range(int(1/self.ItemList.delivery_batches)):
        yield self.env.timeout(self.ItemList.lead_time_func)
        self.inventory += self.num_ordered*self.ItemList.delivery_batches
    #print(f'at {round(self.env.now)} recieved order for {self.num_ordered}')
      self.num_ordered = 0
    
    


class StoreList:
  def __init__(self,env,head):
    self.start_node = head
    self.env = env
    self.total_times = []
    
    self.chain_demand_total = []
    self.obs_cnt = 0
    self.obs_time = []
    self.shop_level = []
    self.depot_level = []
    self.warehouse_level = []

  def insert_at_end(self,process_object):
        new_node = process_object
        if self.start_node is None:
            self.start_node = new_node
            return
        n = self.start_node
        while n.next is not None:
            n= n.next
        n.next = new_node

  def arrayToList(self,arr):
    n = len(arr) 
    
    for i in range(n): 
        self.insert_at_end(arr[i])
    print("All elements linked")   

  def chain_demand(self,m,s):
    return np.random.normal(m,s,1).item()

  def runner_setup(self):
     
    while True:
      #interarrival = self.generate_interarrival()
      #print(interarrival)
      #simulating interrarrival of 1 day eg. demand per day
      interarrival = 1
      yield self.env.timeout(interarrival)
      
      d = self.chain_demand(3,5)
      #self.costs -= self.inventory*2*interarrival
      #self.chain_demand = self.start_node.generate_customer
      self.chain_demand_total.append(d)
      print(f'will now call store supply for store')
      self.env.process(self.start_node.store_supply(d))
  def observe(self):
    
    while True:
      self.obs_cnt += 1
      self.obs_time.append(self.env.now)
      self.shop_level.append(self.start_node.inventory)
      self.depot_level.append(self.start_node.next.inventory)
      self.warehouse_level.append(self.start_node.next.next.inventory)

      
      yield self.env.timeout(1) 
    
  def plot_inventory(self):
    plt.figure()
    plt.plot(self.obs_time,self.shop_level)
    plt.xlabel('Time')
    plt.ylabel('SKU level')
    plt.show()
  
  def plot_depot(self):
    plt.figure()
    plt.plot(self.obs_time,self.depot_level)
    plt.xlabel('Time')
    plt.ylabel('SKU level')
    plt.show()
  
  def plot_warehouse(self):
    plt.figure()
    plt.plot(self.obs_time,self.warehouse_level)
    plt.xlabel('Time')
    plt.ylabel('SKU level')
    plt.show()


def run(simulation,until:float):
    simulation.env.process(simulation.runner_setup())
    simulation.env.process(simulation.observe())

    simulation.env.run(until=until)

#name,ItemList,env,type_store,customerobject=None
c1 = Customer(generate_interarrival,customer_generate_demand)
#name,reorder_level,reorder_qty,demand,std_demand,leadtime,leadtime_std,selling_price,cost_price,demand_func,lead_time_func
i1 = Item('item1',1,60,10,1,400,2,1000,800,generate_demand,generate_leadtime)  
env = simpy.Environment()
s1 = Shop('Shop1',i1,env,'store',c1)
s2 = Shop('Depot1',i1,env,'depot',c1)
s3 = Shop('Warehouse',i1,env,'warehouse',c1)
s = StoreList(env,s1)
s.insert_at_end(s2)
s.insert_at_end(s3)

run(s,360)
#print(s.reorder_function(s.obs_cnt))
s.plot_inventory()


