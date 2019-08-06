package biciMad;


import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

import javax.security.auth.login.FailedLoginException;

/**
 * Hello world!
 */
public final class App {
    private App() {
    }

    /**
     * Says hello to the world.
     * @param args The arguments of the program.
     */
    public static void main(String[] args) {
        System.out.println("Vamos a conectarnos con BiciMad y pedir una apiKey");
        Scanner input = new Scanner(System.in);
        System.out.println("Nombre de usuario: ");
        String user = input.nextLine();
        System.out.println("Contraseña: ");
        String pass = input.nextLine();
        input.close();
        try{
            ApiCon apiCon= new ApiCon(user,pass);
            apiCon.askApiKey();
            System.out.println("Tu apikey es:" + apiCon.getKey());
            System.out.println("La informacion sobre la estacion de Sol: ");
            BiciMadResponse res = apiCon.getBikeStations();
            Map<String, String> station = res.getData()[0];
            for(Map.Entry<String, String> p : station.entrySet()){
                System.out.println(p.getKey()+p.getValue());
            }


        }catch (FailedLoginException  e) {
            System.out.println("La autenticacion con Bicimad Falló:");
            System.out.println(e.getMessage());
        } catch (Exception e) {
            System.out.println("fallo algo mas capullin");
            e.printStackTrace();
        } finally {
            System.out.println("saliendo de la app");
        }


    }
}
