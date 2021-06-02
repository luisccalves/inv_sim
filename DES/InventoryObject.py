import numpy as np
import simpy
import matplotlib.pyplot as plt
import matplotlib as mpl


from Runner import runner
np.random.seed(0)
from math import ceil
from functools import partial
import math

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


class inventory_simulation:

  def __init__(self,env:simpy.Environment,reorder_level:int,reorder_qty:int,purchase_cost:float,selling_price:float,customer_arrival:float,customer_purchase_mean:float,customer_purchase_std:float,reorder_function) -> None:
    self.reorder_level = reorder_level
    
    self.reorder_qty = reorder_qty
    self.costs = 0
    self.revenue = 0
    self.num_ordered = 0
    self.inventory = np.random.uniform(0,self.reorder_qty,1).item()
    self.env = env
    self.obs_time = []
    self.inventory_level = []
    self.demand =0
    self.purchase_cost = purchase_cost
    self.selling_price = selling_price
    self.costslevel = []
    self.saleslevel = []
    self.customer_arrival = customer_arrival
    self.customer_purchase_mean = customer_purchase_mean
    self.customer_purchase_std = customer_purchase_std
    self.holding_cost_unit = .02
    self.holding_cost = []
    self.ordering_cost = 10
    self.other_costs = 4
    self.lead_time_mean = 53
    self.lead_time_std =20
    self.delivery_batches:float = 1
    self.daily_demand_mean = 1
    self.daily_demand_std = 12
    self.service_outage_cnt = 0
    self.totalcost_level= []
    self.demands = []
    self.service_levels_list = []
    self.reorder_function = reorder_function
    self.obs_cnt = 1
    self.safety_stock = int(0.2*self.reorder_function(self.obs_cnt))

    self.inventory_depot= 100

    
  def handle_order(self) -> None:
  
    #print(f'at {round(self.env.now)} placed order for {self.num_ordered}')
    
   
    self.num_ordered = self.reorder_function(self.obs_cnt) + 1 -self.inventory
    self.num_ordered = ceil(self.num_ordered/self.reorder_qty)*self.reorder_qty

    self.costs += self.purchase_cost*self.num_ordered + self.ordering_cost 
    for i in range(int(1/self.delivery_batches)):
      yield self.env.timeout(self.generate_leadtime())
      self.inventory += self.num_ordered*self.delivery_batches
    #print(f'at {round(self.env.now)} recieved order for {self.num_ordered}')
    self.num_ordered = 0
    
  
  def generate_interarrival(self) -> float:
    return np.random.exponential(self.customer_arrival)

  def generate_leadtime(self) -> float:
    __leadtime = np.random.normal(self.lead_time_mean,self.lead_time_std,1).item()
    return(__leadtime if __leadtime>=0 else self.lead_time_mean)

  def customer_generate_demand(self) -> float:
    return np.random.normal(self.customer_purchase_mean,self.customer_purchase_std,1).item()
  def generate_demand(self) -> float:
    __temp =  np.random.normal(self.daily_demand_mean,self.daily_demand_std,1).item()
    return(__temp if __temp>=0 else 0)


  def observe(self):
    
    while True:
      self.obs_cnt += 1
      self.obs_time.append(self.env.now)
      self.inventory_level.append(self.inventory)
      if self.demand > self.inventory: self.service_outage_cnt += 1
      
      
      self.costslevel.append(self.costs)
      self.holding_cost.append(self.inventory * self.holding_cost_unit)
      self.service_levels_list.append(self.service_level)
      
      yield self.env.timeout(1) 

  def runner_setup(self):
    while True:
      #interarrival = self.generate_interarrival()
      #print(interarrival)
      #simulating interrarrival of 1 day eg. demand per day
      interarrival = 1
      yield self.env.timeout(interarrival)
      
      
      #self.costs -= self.inventory*2*interarrival
      self.demand = self.generate_demand()
      self.demands.append(self.demand)
    
      if self.demand < self.inventory:
        self.revenue += self.selling_price*self.demand
        self.inventory -= self.demand
        #print(f'customer comes I sold {self.demand} at time {round(self.env.now,2)}')
      else:
        self.revenue += self.selling_price*self.inventory
        self.inventory = 0 
        #print(f'{self.inventory} is out of stock at {round(self.env.now,2)}')
      if self.inventory <= (self.reorder_function(self.obs_cnt) + self.safety_stock) and self.num_ordered ==0:
        self.env.process(self.handle_order())
  def plot_inventory(self):
    plt.figure()
    plt.plot(self.obs_time,self.inventory_level)
    plt.xlabel('Time')
    plt.ylabel('SKU level')
    plt.show()
  
  def plot_costs(self):
    self.totalcost_level = np.array(self.costslevel)+ np.array(self.holding_cost)
    plt.figure()
    plt.plot(self.obs_time,self.totalcost_level)
    plt.xlabel('Time')
    plt.ylabel('SKU costs USD')
    plt.show()

  def plot_sales(self):
    plt.figure()
    plt.step(self.obs_time,self.costslevel)
    plt.xlabel('Time')
    plt.ylabel('SKU costs USD')

  def plot_holding(self):
    plt.figure()
    plt.step(np.arange(len(self.holding_cost)),self.holding_cost)
    plt.xlabel('Time')
    plt.ylabel('holding costs')
  def plot_demand(self):
    plt.figure()
    plt.step(np.arange(len(self.demands)),self.demands)
    plt.xlabel('Time')
    plt.ylabel('Demands')
  def plot_serviceLevels(self):
    plt.figure()
    plt.plot(np.arange(len(self.service_levels_list)),self.service_levels_list)
    plt.xlabel('Time')
    plt.ylabel('Demands')
    plt.show()

  def zero_inventory_level(self):
    __temp_level= np.array(self.inventory_level)
    __temp_level1 = __temp_level[__temp_level==0]
    if len(__temp_level1)==0:
      return 1
    else:
      return (1 - len(__temp_level1)/len(__temp_level))

 
   

  def avg_cost_of_inventory(self):
    __temp_level = np.array(self.inventory_level)*self.purchase_cost
    return (__temp_level.mean())

  @property
  def service_level(self):
    
    return 1-self.service_outage_cnt/(max(self.obs_time)+1)


def run(simulation:inventory_simulation,until:float):
  simulation.env.process(simulation.runner_setup())
  simulation.env.process(simulation.observe())

  simulation.env.run(until=until)




s = inventory_simulation(simpy.Environment(),20,30,1240,1350,1,10,5,rol)
run(s,360)
#print(s.reorder_function(s.obs_cnt))
s.plot_costs()








def eoq_sim_search(reorder_lvl_proposals:float,reorder_qty_proposals:np.array,purchase_cost:float,selling_price:float,run_time:int,target_service_level:float) -> float:
  service_levels = []
  costs = []

  eoq = []
  
  for q in reorder_qty_proposals:
      s = inventory_simulation(simpy.Environment(),reorder_lvl_proposals,q,purchase_cost,selling_price,0.3,10,5)
      run(s,run_time)
      service_levels.append(s.service_level())
      costs.append(s.avg_cost_of_inventory())
      
      eoq.append(q)
  
  service_levels = np.array(service_levels)
  costs = np.array(costs)
  eoq = np.array(eoq)
  target_service_level = min(max(service_levels),target_service_level)
  print(costs)
  print(service_levels)
  print(eoq)
  
  if (len(service_levels)<1) or (len(costs)<1) or (len(eoq)<1) or len(np.where(service_levels>=target_service_level)) < 1:
    return False
  else:
    fig, axs = plt.subplots(3)

    axs[0].plot(costs,service_levels)
    
    axs[1].plot(eoq,costs)
    axs[2].plot(eoq,service_levels)
    
    return eoq[np.where(costs==np.min(costs[service_levels>=target_service_level]))][0]
    plt.show()

#eoq_sim_search(8,[25,35,45,60,100,150,200,250],50,100,10,0.5)
