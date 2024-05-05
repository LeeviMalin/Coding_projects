/*Ristinolla
 *  Kuvaus:
 *   Ohjelma toteuttaa ristinollapelin, jossa pelialuetta pystyy
 * laajentamaan. Alussa peliruudukko on kooltaan 3 x 3. Peliruudukossa
 * on kolmenlaisia merkkejä: risti (X), nolla (0) ja tyhjä (.).
 *   Pelivuorossa ovat vuorotellen risti ja nolla, risti aloittaa.
 * Joka kierroksella vuorossa olevalle merkille kysytään koordinaatteja
 * eli kahta lukua. Vuorossa oleva merkki sijoitetaan peliruudukolla
 * annettuihin koordinaatteihin, ja vuoro siirtyy toiselle merkille.
 *   Pelin voittaa merkki, jolla saadaan ensimmäiseksi täytettyä peliruudukon
 * kokonainen rivi, kokonainen sarake tai kokonainen diagonaali.
 * Peli voi päättyä myös sellaiseen tilanteeseen, että peliruudukko on
 * täynnä merkkejä, mutta kumpikaan merkki ei voittanut.
 *   Ohjelma tarkistaa annetut koordinaatit. Koordinaattien pitää olla
 * peliruudukon sisällä, tai koordinaatit saavat ylittyä tai alittua
 * korkeintaan yhdellä. Jos annettu x- tai y-koordinaatti (rivi tai sarake)
 * ylittyy yhdellä, peliruudukko laajenee oikealle ja alaspäin. Jos taas
 * x- tai y-koordinaatti alittuu yhdelle, peliruudukko laajenee vasemmalle
 * ja alaspäin. Peliruudukko siis pysyy aina neliön muotoisena.
 *   Pelin päättyessä kerrotaan, kumpi voitti, vai voittiko kumpikaan.
 *
 * */

#include <iostream>
#include <vector>
#include <cctype>

using namespace std;

void print_board(vector <vector <char>> y_vektori,int koko) {
    //funktio tulostaa 3x3 pelilaudan ja akselien numerot
    // Parametrit: y vektori ja laudan koko
    // ei paluuarvoa
    cout << "  ";
    for (int x = 1 ; x <= koko ; ++x) {
        cout << x % 10 << " ";
    }
    cout << endl;
    for (int y = 1 ; y <= koko ; ++y) {
        cout << y % 10 << " ";
        for (int x = 1 ; x <= koko ; ++x) {
            cout << y_vektori.at(y).at(x) << " ";
        }
        cout << endl;
    }
    cout << endl;
}

bool check_input(vector <vector <char>> y_vektori, int& x,int& y,int koko, char vuoro) {
    // tarkistaa käyttäjän syötteen ja tallentaa sen x ja y muuttujiin.
    // parametrit: y vektori, x ja y koordinaatit , laudan koko ja vuorossa oleva merkki
    // palauttaa false jos syötteenä on q
    // palauttaa true kun annetut koordinaatit kelpaavat

    string x_annettu;
    string y_annettu;
    int tarkistus_muuttuja = 0;

    while (true) {
        tarkistus_muuttuja = 0;
        cout << "For " << vuoro << ", enter coordinates: x y> ";
        cin >> x_annettu;
        // tarkistetaan onko ensimmäiseksi annettu merkki q jolloin
        // funktio palauttaa false
        if (x_annettu == "q") {
            cout << "Why on earth you are giving up the game?" << endl;
            return false;
        }
        cin >> y_annettu;
        // tarkastetaan onko annetuissa syötteissä muuta kuin
        // numero merkkejä.
        for (char merkki : x_annettu) {
            if (static_cast<int>(merkki) > 58) {
                tarkistus_muuttuja += 1;
            }
        }
        for (char merkki : y_annettu) {
            if (static_cast<int>(merkki) > 58) {
                tarkistus_muuttuja += 1;
            }
        }
        if (tarkistus_muuttuja != 0) {
            cout << "Coordinate outside the board" << endl;
            continue;
        }

        x = stoi(x_annettu);
        y = stoi(y_annettu);

        // tarkastaa onko annetuissa koordinaateissa jo merkki
        if (x <= koko and y <= koko) {
            if (y_vektori.at(y).at(x) != '.') {
                cout << "The given place is already occupied" << endl;
                continue;
            }
        }
        // tarkastaa onko annetut luvut laudan ulkopuolella
        if (y == 0 and x == koko + 1) {
        }
        else if (y == koko + 1 and x == 0) {
        }
        else if (0 <= x and x <= koko + 1 and 0 <= y and y <= koko + 1) {
                    return true;          
        }
        cout << "Coordinate outside the board" << endl;
    }
}

void place_mark(vector <vector <char>>& y_vektori, int x, int y, char vuoro) {
    // Tallentaa vuorossa olevan merkin oikeaan paikkaan.
    // Parametrit: y vektori, x ja y koordinaatit ja vuorossa oleva merkki
    // ei paluuarvoa

    // Lisää yhden molempii koordinaatteihin ruudukon laajentuessa vasemmalle ja ylös
    // jotta koordinaatit tulostuisi oikein
    if (x == 0 or y == 0) {
        x += 1;
        y += 1;
    }
    y_vektori.at(y).at(x) = vuoro;
    if (x == 0 or y == 0) {
        cout << "ses" << endl;
    }
 }

void increase_size (vector <vector <char>>& y_vektori,int x,int y,int koko) {
    // Kasvattaa laudan kokoa joko vasemmalle ylös tai oikealle alas.
    // parametrit: y vektori, x ja y koordinaatit ja laudan koko
    // ei paluuarvoa

    // Luodaan oikean kokoinen tyhjä vektori mikä
    // lisätään myöhemmin y vektoriin
    vector <char> tyhja_vektori;

    for (int n = 0 ; n <= koko ; ++n) {
        tyhja_vektori.push_back('.');
    }

    // kasvattaa ruudokkoa oikealle ja alas lisäämällä jokaisen
    // x vektorin perään merkin '.' ja tyhjän vektorin y vektorin perään
    if (x != 0 and y != 0) {
        for (int n = 0 ; n < koko ; ++n) {
            y_vektori.at(n).push_back('.');
        }
        y_vektori.push_back((tyhja_vektori));
    }
    // Kasvattaa ruudukkoa vasemmalle ja ylös. Tämän
    // toteutukseen on käytetty iteraattoreita ja insert komentoa
    else {
        for (int n = 0 ; n < koko ; ++n) {
            vector <char>::iterator it = y_vektori.at(n).begin();
            y_vektori.at(n).insert(it,'.');
        }
        vector <vector <char>>::iterator y_it = y_vektori.begin();
        y_vektori.insert(y_it,tyhja_vektori);
    }
}


int check_win(vector <vector <char>> y_vektori, int koko) {
    // Tarkastelee eri voittotilanteet. Tämä on toteutettu vertaamalla rivin
    // merkkejä rivin ensimmäiseen merkkiin ja laskemalla kuinka moni täsmää
    // ja vertaamalla lukemaa rivin pituuteen.
    // parametrit: y vektori ja laudan koko
    // paluuarvona 0,1,2 tai 3 riippuen siitä mikä rivi voittaa pelin

    char tarkistus;
    int rivissa;

    // tarkistaa vaakarivit
    for (int y = 1 ; y <= koko ; ++y) {
        rivissa = 0;
        tarkistus = y_vektori.at(y).at(1);
        for (char merkki : y_vektori.at(y)) {
            if (merkki == tarkistus) {
                rivissa += 1;
            }
            if (tarkistus != '.' and rivissa == koko) {
                return 1;
            }
        }
    }
    // tarkistaa pystyrivit
    for (int x = 1 ; x <= koko ; ++x) {
        rivissa = 0;
        tarkistus = y_vektori.at(1).at(x);
        for (int y = 1 ; y <= koko ; ++y) {
            if (y_vektori.at(y).at(x) == tarkistus) {
                rivissa += 1;
            }
            if (tarkistus != '.' and rivissa == koko) {
                return 2;
            }
        }
    }
    // tarkistaa vinot rivit
    rivissa = 0;
    for (int n = 1 ; n <= koko ; ++n) {
        tarkistus = y_vektori.at(1).at(1);
        if (tarkistus == y_vektori.at(n).at(n)) {
            rivissa += 1;
        }
        if (tarkistus != '.' and rivissa == koko) {
            return 3;
        }
    }
    rivissa = 0;
    for (int n = 1 ; n <= koko ; ++n) {
         int x = koko + 1 - n;
         tarkistus = y_vektori.at(1).at(koko);
         if (tarkistus == y_vektori.at(n).at(x)) {
             rivissa += 1;
         }
         if (tarkistus != '.' and rivissa == koko) {
             return 3;
         }
    }
    return 0;
}

bool check_full(vector <vector <char>> y_vektori,int koko) {
    // Tarkastaa onko ruudukko täynnä. Toteutettu laskemalla jokainen
    // x tai 0 merkki laudalla ja vertaamalla lukemaa laudan kokoon.
    // parametrit: y vektori ja laudan koko
    // paluuarvona true tai false

    int merkki_laskuri = 0;

    for (int y = 1 ; y <= koko ; ++y) {
        for (int x = 1 ; x <= koko ; ++x) {
            if (y_vektori.at(y).at(x) != '.') {
                merkki_laskuri += 1;
            }
            if (merkki_laskuri == koko * koko) {
                return true;
            }
        }
    }
    return false;
}

int main()
{
    vector <char> x_vektori;
    vector <vector <char>> y_vektori;
    int koko = 3;
    char vuorossa = '0';
    int x_koord;
    int y_koord;
    string voittaja;
    string voittaja_X = "Cross";
    string voittaja_0 = "Nought";

    // Luodaan vektorit joihin tallenetaan pelilaudan tiedot
    // x vektoriin tallennetaan merkit (char) ja y vektoriin x vektorit
    for (int j = 0 ; j <= koko ; ++j) {
        x_vektori.push_back('.');
    }
    for (int i = 0 ; i <= koko ; ++i) {
        y_vektori.push_back(x_vektori);
    }
    cout << "Start game:" << endl;
    print_board(y_vektori,koko);

    while (true) {
        if (vuorossa == '0') {
            vuorossa = 'X';
        }
        else {
            vuorossa = '0';
        }
        // koordinaattien luku
        if (check_input(y_vektori,x_koord,y_koord,koko,vuorossa) == false) {
            return EXIT_SUCCESS;
        }
        // kasvatetaan ruudukkoa tarvittaessa, piirretään merkit ja tulostetaan pelilauta
        if (x_koord == koko + 1 or y_koord == koko + 1 or x_koord == 0 or y_koord == 0) {
            koko += 1;
            increase_size(y_vektori,x_koord,y_koord,koko);           
        }
        place_mark(y_vektori,x_koord,y_koord,vuorossa);
        print_board(y_vektori,koko);
        // täyden laudan tarkastelu
        if (check_full(y_vektori,koko) == true) {
                cout << "No empty places" << endl;
                cout << "Game over!" << endl;
                return EXIT_SUCCESS;
        }
        // voiton tarkastelu
        int voitto_numero = check_win(y_vektori,koko);
        if (voitto_numero == 0) {
            continue;
        }
        if (vuorossa == '0') {
            voittaja = voittaja_0;
        }
        if (vuorossa == 'X') {
            voittaja = voittaja_X;
        }
        if (voitto_numero == 1) {
            cout << voittaja << " won horizontally" << endl;
            cout << "Game over!" << endl;
            return EXIT_SUCCESS;        }
        if (voitto_numero == 2) {
            cout << voittaja << " won vertically" << endl;
            cout << "Game over!" << endl;
            return EXIT_SUCCESS;        }
        if (voitto_numero == 3) {
            cout << voittaja << " won diagonally" << endl;
            cout << "Game over!" << endl;
            return EXIT_SUCCESS;        }
    }
}
