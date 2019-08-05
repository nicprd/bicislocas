package biciMad;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;




public class Request{

    public static HttpURLConnection get(URL url, Map<String, String> headers) throws IOException {
        HttpURLConnection con = (HttpURLConnection)url.openConnection();
        con.setRequestMethod("GET");
        for(Map.Entry<String,String> entry: headers.entrySet()){
            con.setRequestProperty((String)entry.getKey(), (String)entry.getValue());
        }
        con.getResponseCode();
        return con;
    }

    public static String getContent(HttpURLConnection con) throws IOException{
        StringBuffer content = new StringBuffer();
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(con.getInputStream())); //transforma stream de bytes en stream de caracteres
        String l ;
        while((l = reader.readLine()) != null){
            content.append(l);
        } reader.close();
        return content.toString();
    }
}

