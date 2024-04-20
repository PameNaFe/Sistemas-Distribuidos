import java.rmi.Remote;
import java.rmi.RemoteException;

public interface CuentaService extends Remote {
    	boolean registrar(String usuario, String contraseña) throws RemoteException;
    	boolean iniciarSesion(String usuario, String contraseña) throws RemoteException;
    	void cerrarSesion(String usuario) throws RemoteException;
	boolean actualizarDatos(String usuario, String nuevaContraseña) throws RemoteException;

}

