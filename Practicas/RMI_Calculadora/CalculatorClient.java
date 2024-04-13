import java.rmi.Naming;
import java.util.Scanner;

public class CalculatorClient {
    public static void main(String[] args) {
        try {
            CalculatorInterface calc = (CalculatorInterface) Naming.lookup("rmi://localhost/CalculatorService");
            Scanner scanner = new Scanner(System.in);
            System.out.print("Valor de a: ");
            double a = scanner.nextDouble();
            System.out.print("Valor de b: ");
            double b = scanner.nextDouble();

            System.out.println("Suma: " + calc.add(a, b));
            System.out.println("Resta: " + calc.subtract(a, b));
            System.out.println("Multiplicacion: " + calc.multiply(a, b));
            System.out.println("Division: " + calc.divide(a, b));

            scanner.close();
        } catch (Exception e) {
            System.err.println("Algo pasó: " + e.toString());
            e.printStackTrace();
        }
    }
}

