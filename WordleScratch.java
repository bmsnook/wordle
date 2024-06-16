import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Scanner;
import java.io.File;
import java.util.Random;
import java.io.*;
import java.util.*;

public class WordleScratch {
    static ArrayList<String> wordsFr = new ArrayList<String>(Arrays.asList("un", "deux", "trois", "quatre", "cinq"));
    static ArrayList<String> wordsDe = new ArrayList<String>(Arrays.asList("eins", "zwei", "drei", "vier", "fünf"));
    static ArrayList<String> wordsEs = new ArrayList<String>(Arrays.asList("uno", "dos", "tres", "cuatro", "cinco"));

    //static String[] wordsFr = {"un", "deux", "trois", "quatre", "cinq"};
    //static String[] wordsDe = {"eins", "zwei", "drei", "vier", "fünf"};
    //static String[] wordsEs = {"uno", "dos", "tres", "cuatro", "cinco"};

//  static ArrayList<String[]> allLangs = new ArrayList<String[]>;
//  allLangs.add(wordsFr);
//  allLangs.add(wordsDe);
//  allLangs.add(wordsEs);

    private static String pickRandFromArray(ArrayList<String> thisArray) {
    //private static String pickRandFromArray(String[] thisArray) {
        Random rand = new Random();
        int n = rand.nextInt(thisArray.size());
        //int n = rand.nextInt(thisArray.length);
//      n += 1;
        return thisArray.get(n);
    }

    public static void main(String[] args) {
        // Array has parameter "length"
        //System.out.println(String.format("Length of %s is %s",wordsFr,wordsFr.length));
        //System.out.println(String.format("Length of %s is %s",wordsDe,wordsDe.length));
        //System.out.println(String.format("Length of %s is %s",wordsEs,wordsEs.length));
        // ArrayList has method "size()"
        System.out.println(String.format("Size of %s is %s",wordsFr,wordsFr.size()));
        System.out.println(String.format("Size of %s is %s",wordsDe,wordsDe.size()));
        System.out.println(String.format("Size of %s is %s",wordsEs,wordsEs.size()));

        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsFr));
        }
        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsDe));
        }
        for (int i=1; i<=10; i++) {
            System.out.println(pickRandFromArray(wordsEs));
        }
        Set<String> s = new HashSet<String>();
        s.add("Welcome");
        s.add("To");
        s.add("Geeks");
        s.add("4");
        s.add("Geeks");
        s.add("Set");
        System.out.println("Set: " + s);
        System.out.println("Set contains 'geeks': " + s.contains("geeks"));
        System.out.println("Set contains 'nerds': " + s.contains("nerds"));
        System.out.println("Set contains 'Geeks': " + s.contains("Geeks"));
        System.out.println("Set size is: " + s.size());

        System.out.println("ArrayList(De) contains 'funf': " + wordsDe.contains("funf"));
        System.out.println("ArrayList(De) contains 'Fünf': " + wordsDe.contains("Fünf"));
        System.out.println("ArrayList(De) contains 'fünf': " + wordsDe.contains("fünf"));
    }
}

