package biciMad;

import java.util.Map;

import com.google.gson.Gson;

public class BiciMadResponse {
    String code;
    Map<String, String> data[];
    
    public static BiciMadResponse BiciMad(String content){
        Gson gson = new Gson();
        return gson.fromJson(content, BiciMadResponse.class);
    }

    public String getCode(){
        return code;
    }

    public Map<String, String>[] getData(){
        return data;
    }
}