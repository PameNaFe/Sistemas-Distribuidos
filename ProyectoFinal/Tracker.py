from __future__ import print_function
import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Tracker(object):
    def _init_(self):
        self.resources = {}
        self.hosts = {}

    def getResource(self, resource):
        resource_hosts = self.resources.get(resource)
        resource_info = []
        for i in 0,len(resource_hosts)-2:
            host_ip = self.hosts.get(resource_hosts[i])
            resource_info.append(host_ip)
        resource_info.append(resource_hosts[-1])
        return resource_info

    def putResource(self, name, resources):
        for resource in resources:
            new_resource = self.resources.get(resource)
            if new_resource == None:
                new_resource.update(resource = [name]) 
            else:
                new_resource.insert(0, name)
                self.resources.update(resource = new_resource)
            print("Nuevo recurso asociado")
            print("Host: "+ name)
            print("Recurso actualizado: "+ new_resource)  
     
    def identifyHost(self, name, ip, resources):
        print("Nuevo host identificado: ")
        print("Nombre: "+ name + "   IP: " + ip)
        self.hosts[name] = ip
        self.putResource(name, resources)
        


def main():
    Pyro4.Daemon.serveSimple(
        {Tracker: "tracker"},
        host="localhost",
        port=55300,
        ns=True
    )
    #daemon = Pyro4.Daemon()
    #uri = daemon.register(Tracker)
    #print(uri)

if __name__ == "_main_":
    print("es main")
    main()