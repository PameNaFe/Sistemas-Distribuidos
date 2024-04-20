import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.HashMap;
import java.util.Map;

public class CuentaServiceImpl extends UnicastRemoteObject implements CuentaService {
    private Map<String, String> usuariosContrasenas;

    protected CuentaServiceImpl() throws RemoteException {
        super();
        usuariosContrasenas = new HashMap<>();
    }

    @Override
    public synchronized boolean registrar(String usuario, String contraseña) throws RemoteException {
        if (!usuariosContrasenas.containsKey(usuario)) {
            usuariosContrasenas.put(usuario, contraseña);
            System.out.println("Usuario registrado correctamente.");
            return true;
        } else {
            System.out.println("El usuario ya existe.");
            return false;
        }
    }

    @Override
    public synchronized boolean iniciarSesion(String usuario, String contraseña) throws RemoteException {
        if (usuariosContrasenas.containsKey(usuario) && usuariosContrasenas.get(usuario).equals(contraseña)) {
            System.out.println("Inicio de sesión exitoso.");
            return true;
        } else {
            System.out.println("Nombre de usuario o contraseña incorrectos.");
            return false;
        }
    }

    @Override
    public synchronized void cerrarSesion(String usuario) throws RemoteException {
        System.out.println("Sesión cerrada para el usuario: " + usuario);
    }

public synchronized boolean actualizarDatos(String usuario, String nuevaContraseña) throws RemoteException {
        if (usuariosContrasenas.containsKey(usuario)) {
            usuariosContrasenas.put(usuario, nuevaContraseña);
            System.out.println("Datos actualizados correctamente.");
            return true;
        } else {
            System.out.println("El usuario no existe.");
            return false;
        }
    }
}

