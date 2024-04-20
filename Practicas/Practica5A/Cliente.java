import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Scanner;

public class Cliente {
    public static void main(String[] args) {
        try {
            // Localizar el registro RMI en el servidor
            Registry registry = LocateRegistry.getRegistry("localhost",1099);

		    // Buscar los proveedores en el registro RMI
		    TiendaOnline proveedorCompra = (TiendaOnline) registry.lookup("Compra");
		    TiendaOnline proveedorCarrito = (TiendaOnline) registry.lookup("Carrito");
		    TiendaOnline proveedorVerCarrito = (TiendaOnline) registry.lookup("VerCarrito");
		    TiendaOnline proveedorPagar = (TiendaOnline) registry.lookup("Pagar");

		    // Realizar operaciones con los proveedores
		    System.out.println("Resultado del proveedor de compra: " + proveedorCompra.comprar("Producto1"));
		    System.out.println("Resultado del proveedor de carrito: " + proveedorCarrito.agregarAlCarrito("Producto2"));
		    System.out.println("Resultado del proveedor de ver carrito: " + proveedorVerCarrito.verCarrito());
		    System.out.println("Resultado del proveedor de pagar: " + proveedorPagar.pagar());

	// Nuevo servicio:


  	CuentaService cuentaService = (CuentaService) registry.lookup("CuentaService");

  	Scanner scanner = new Scanner(System.in);
        int opcion;

	do {
                // Mostrar menú
		System.out.println("");
                System.out.println("Seleccione una opción:");
                System.out.println("1. Inicio de sesión");
                System.out.println("2. Nuevo usuario");
                System.out.println("3. Cerrar sesión");
                System.out.println("4. Actualizar información");
                System.out.println("0. Salir");

                // Leer la opción del usuario
                opcion = scanner.nextInt();
                scanner.nextLine(); // Limpiar el buffer de entradA

		switch (opcion) {
                    case 1:

                        iniciarSesion(cuentaService, scanner);
                        break;
                    case 2:
                        registrarUsuario(cuentaService, scanner);
                        break;
                    case 3:
                        cerrarSesion(cuentaService, scanner);
                        break;
		    case 4:
			actualizarDatos(cuentaService, scanner);
			break;
                    case 0:
                        System.out.println("Saliendo del programa.");
                        break;
                    default:
                        System.out.println("Opción no válida. Por favor, seleccione nuevamente.");
                        break;
		}
	} while (opcion != 0);
		
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }

	private static void iniciarSesion(CuentaService cuentaService, Scanner scanner) throws Exception {
        System.out.println("Inicio de sesión:");
        System.out.println("Ingrese su nombre de usuario:");
        String usuario = scanner.nextLine();
        System.out.println("Ingrese su contraseña:");
        String contraseña = scanner.nextLine();
        boolean inicioSesion = cuentaService.iniciarSesion(usuario, contraseña);
        if (inicioSesion) {
            System.out.println("Inicio de sesión exitoso.");
        } else {
            System.out.println("Nombre de usuario o contraseña incorrectos.");
        }
    }

	private static void registrarUsuario(CuentaService cuentaService, Scanner scanner) throws Exception {
		System.out.println("Registro de nuevo usuario:");
		System.out.println("Ingrese su nombre de usuario:");
		String usuario = scanner.nextLine();
		System.out.println("Ingrese su contraseña:");
		String contraseña = scanner.nextLine();
		boolean registrado = cuentaService.registrar(usuario, contraseña);
		if (registrado) {
		    System.out.println("Usuario registrado correctamente.");
		} else {
		    System.out.println("El usuario ya existe.");
		}
	    }

private static void cerrarSesion(CuentaService cuentaService, Scanner scanner) throws Exception {
        System.out.println("Cerrar sesión:");
        System.out.println("Ingrese su nombre de usuario:");
        String usuario = scanner.nextLine();
        cuentaService.cerrarSesion(usuario);
        System.out.println("Sesión cerrada correctamente.");
    }

private static void actualizarDatos(CuentaService cuentaService, Scanner scanner) throws Exception {
        System.out.println("Actualizar contraseña:");
        System.out.println("Ingrese su nombre de usuario:");
        String usuario = scanner.nextLine();
        System.out.println("Ingrese su nueva contraseña:");
        String nuevaContraseña = scanner.nextLine();
        boolean actualizado = cuentaService.actualizarDatos(usuario, nuevaContraseña);
        if (actualizado) {
            System.out.println("Contraseña actualizada correctamente.");
        } else {
            System.out.println("No se pudo actualizar la contraseña. Verifique el nombre de usuario.");
        }
    }
}
