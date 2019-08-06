package biciMad;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import javax.security.auth.login.FailedLoginException;

public class ApiCon {
    static String sourceUrl = 
        "https://openapi.emtmadrid.es/v1/";
    static String loginUrl = "mobilitylabs/user/login/";
    static String stationsUrl = "transport/bicimad/stations/";


    private String user;
    private String pass;
    protected String apiKey;

    public ApiCon(String user, String pass) {
        this.user = user;
        this.pass = pass;
        this.apiKey = "";
    }
    private BiciMadResponse login() throws IOException{
        Map<String,String> headers = new HashMap<String, String>();
        headers.put("email",user);
        headers.put("password", pass);
        HttpURLConnection res = 
            Request.get(new URL(sourceUrl+loginUrl), headers);  
        return BiciMadResponse.BiciMad(
            Request.getContent(res));
    }

    public void askApiKey() throws FailedLoginException, IOException {
        BiciMadResponse log = login();
        if(!(log.getCode().equals("00") || log.getCode().equals("01")) ){
            throw new FailedLoginException("BiciMad respondio con: "+log.getCode());
        }
        apiKey = log.getData()[0].get("accessToken");
    }

    public String getKey(){
        return apiKey;
    }

    public BiciMadResponse getBikeStations()throws IOException{
        BiciMadResponse res = 
        BiciMadResponse.BiciMad(
            Request.getContent(
                Request.get(
                    new URL(sourceUrl + stationsUrl),
                    new HashMap<String, String>(){
                        private static final long serialVersionUID = 1L;
					{
                        put("accessToken", apiKey);
                    }
            })));
        return res;
    }
}