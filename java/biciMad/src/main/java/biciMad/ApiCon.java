package biciMad;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import javax.security.auth.login.FailedLoginException;

public class ApiCon {
    String sourceUrl = 
        "https://openapi.emtmadrid.es/v1/mobilitylabs/";
    String loginUrl = "user/login/";
    private String user;
    private String pass;
    protected String apiKey;

    public ApiCon(String user, String pass) throws FailedLoginException, MalformedURLException, IOException {
        this.user = user;
        this.pass = pass;
        this.apiKey = askApiKey();
    }
    private BiciMadResponse login() throws MalformedURLException, IOException{
        Map<String,String> headers = new HashMap<String, String>();
        headers.put("email",user);
        headers.put("password", pass);
        HttpURLConnection res = Request.get(
        new URL(sourceUrl+loginUrl), headers);  

        return BiciMadResponse.BiciMad(
            Request.getContent(res));
    }

    private String askApiKey() throws FailedLoginException, MalformedURLException, IOException {
        BiciMadResponse log = login();
        if(!(log.getCode().equals("00") || log.getCode().equals("01")) ){
            throw new FailedLoginException(log.getCode());
        }
        String key = log.getData()[0].get("accessToken");
        return key;
    }

    public String getKey(){
        return apiKey;
    }
}