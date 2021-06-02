class runner:
    def __init__(self,simulation_agent):
        self.simulation_agent = simulation_agent
    def select_process_run(self,process_name):
        pass
        
    def run(self,until:float):
        self.simulation_agent.env.process(self.simulation_agent.runner_setup())
        self.simulation_agent.env.process(self.simulation_agent.observe())

        self.simulation_agent.env.run(until=until)

        