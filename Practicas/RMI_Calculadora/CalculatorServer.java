import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class CalculatorServer extends UnicastRemoteObject implements CalculatorInterface {

    protected CalculatorServer() throws RemoteException {
        super();
    }

    public double add(double a, double b) throws RemoteException {
        return a + b;
    }

    public double subtract(double a, double b) throws RemoteException {
        return a - b;
    }

    public double multiply(double a, double b) throws RemoteException {
        return a * b;
    }

    public double divide(double a, double b) throws RemoteException {
        if (b == 0) {
            throw new RemoteException("La diviso entre cero es invallida");
        }
        return a / b;
    }

    public static void main(String[] args) {
        try {
            java.rmi.registry.LocateRegistry.createRegistry(1099);
            CalculatorServer server = new CalculatorServer();
            java.rmi.Naming.rebind("CalculatorService", server);
            System.out.println("Calculadora en funcionamiento");
        } catch (Exception e) {
            System.err.println("Calculator server exception: " + e.toString());
            e.printStackTrace();
        }
    }
}

