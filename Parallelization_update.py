import pygmo as pg
import time



def compute(w,h,d):
    #This function will send parameters to FEM code. 
    #Emulating this simple problem for now.
    volume=w*h*d
    surfarea=2*(w*h + h*d + d*w)
    seconds=1000000  #Adding Artificial Delay to emulate external software delay.
    time.sleep(seconds/1000000.0)
    print(w,h,d)
    return volume,surfarea


class cuboid():
    def fitness(self, x):
        w, h, d = x #unpack elements
        volume,surfarea=compute(w,h,d)
        #OBJECTIVE 1: minimize volume
        
        O1 = volume
        
        #OBJECTIVE 2: maximize total surface area
        O2 = surfarea
       
        return [O1, -O2]

    def get_nic(self):
        return 0

    def get_nec(self):
        return 0

    def get_nobj(self):
        return 2

    def get_name(self):
        return "Cuboid Function"

    def get_bounds(self):
        wl, hl, dl = 0.5, 0.1, 0.25 #lower limits
        wu, hu, du = 10, 3, 5 #upper limits
        return ([wl, hl, dl],[wu, hu, du])

def main():
    prob = pg.problem(cuboid())

    nsga=pg.nsga2(gen=48) #Using nsga2 as it supports bfe and multiobjective optimization
    nsga.set_bfe(pg.bfe())
    algo=pg.algorithm(nsga)
    #ils = pg.island(algo=algo,prob=prob,size=48,udi=pg.mp_island()) #This is working
    ils = pg.island(algo=algo,prob=prob,size=48,udi=pg.mp_island(), b=pg.default_bfe())  #Upon running this line, the CPU usage increases to 100% and it's stuck
    ils.evolve()
    pop=ils.get_population()
    
    return pop
    #I haven't evolved the island as I am facing issue in the above step itself.
    

if __name__=="__main__":
    print("Calling Main function" )
    pop=main()
    pg.mp_island.shutdown_pool()
    pg.mp_bfe.shutdown_pool()
