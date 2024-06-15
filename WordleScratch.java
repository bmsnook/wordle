import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Scanner;
import java.io.File;
import java.util.Random;

public class WordleScratch {
    //ArrayList<String> wordsFr = new ArrayList<String>();
    //ArrayList<String> wordsDe = new ArrayList<String>();
    //ArrayList<String> wordsEs = new ArrayList<String>();
    static String[] wordsFr = {"un", "deux", "trois", "quatre", "cinq"};
    static String[] wordsDe = {"eins", "zwei", "drei", "vier", "fünf"};
    static String[] wordsEs = {"uno", "dos", "tres", "cuatro", "cinco"};

//  static ArrayList<String[]> allLangs = new ArrayList<String[]>;
//  allLangs.add(wordsFr);
//  allLangs.add(wordsDe);
//  allLangs.add(wordsEs);

    //private static String pickRandFromArray(ArrayList<String> thisArray) {
    private static String pickRandFromArray(String[] thisArray) {
        Random rand = new Random();
        //int n = rand.nextInt(thisArray.size());
        int n = rand.nextInt(thisArray.length);
//      n += 1;
        return thisArray[n];
    }

    public static void main(String[] args) {
        System.out.println(String.format("Length of %s is %s",wordsFr,wordsFr.length));
        System.out.println(String.format("Length of %s is %s",wordsDe,wordsDe.length));
        System.out.println(String.format("Length of %s is %s",wordsEs,wordsEs.length));

        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsFr));
        }
        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsDe));
        }
        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsEs));
        }
    }
}

