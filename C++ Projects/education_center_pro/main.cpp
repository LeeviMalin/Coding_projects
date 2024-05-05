/* 
 *
 * Kuvaus:
 *      Koodi toteuttaa ohjelman, joka lukee tiedostosta kurssikeskuksen
 *  kurssitietoja ja tallentaa ne map<string,vector<Course>> tietorakenteeseen.
 *  Course on struct tyyppinen rakenne joka tallentaa kursseista tiedot:
 *   nimi
 *   sijainti
 *   osallistujamäärä
 *
 *  Kursseista voi etsiä tietoa komennoilla:
 *      Themes
 *       - tulostaa saatavilla olevien kurssien teemat
 *      Courses
 *       - tulostaa käyttäjän antamilla paikkakunnan ja teeman avulla
 *         saatavilla olevien kurssien nimet ja niiden osallistujamäärät
 *      available
 *       - tulostaa kurssien joissa on tilaa tiedot
 *      courses_in_theme
 *       - tulostaa kaikki käyttäjän antamaan teemaan liittyvät kurssit
 *      courses_in_location
 *       - tulostaa kaikki käyttäjän antamassa sijainnissa olevat kurssit
 *      favorite_theme
 *       - tulostaa suosituimman teeman tai teemojen osallistuja määrän
 *  Ohjelmassa on myös komento cancel joka poistaa käyttäjän antamalla nimellä kaikki
 *  kurssit
 *
 *
 * Totetutuksesta:
 *  Suurin osa hakualgoritmeistä on toteutettu tallentamalla ensin haluttu tieto
 *  set tai map rakenteeseen jotta se saadaan aakkosjärjestykseen ja erikseen tulostettu
 *  tallennetut tiedot. Välitallentamisen ylimääräisen tietorakenteeseen olisi voinut
 *  voinut ehkä välttää paremmalla tietorakenteen valinnalla, mutta tajusin asian
 *  liian möhäisessä vaiheessa.
 *  Qt creator antaa for silmukoista varoituksen kun luettava tietotyyppi on monimutkaisempi esim.
 *  for (pair<string,vector<Course>> pari : kurssi_kirjasto) antaa varoituksen. Googlauksien perusteella
 *  ongelma liittyy viittamiisen tietorakennetta luettaessa mutta en saanut varoituksia
 *  korjattua viittaamalla & merkillä.
 *
 */
#include <algorithm>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <map>
#include <set>

using namespace std;

const int COURSE_FULL = 50;
const char DELIMETER = ';';

struct Course {
    string nimi;
    string sijainti;
    int osallistujat;
};

// Jakaa annetun merkkijonon str annetun merkin delimiter erottelemiin osiin
// ja palauttaa osat vektorissa.
// Jos erotinmerkki on lainausmerkkien sisällä, erotinmerkistä ei välitetä,
// eli osaa olla erottelematta lainausmerkkien sisällä olevan tekstin.

std::vector<std::string> split_ignoring_quoted_delim(const std::string& str, char delimiter)
{
    std::vector<std::string> result = {""};
    bool inside_quotation = false;
    for(char current_char : str)
    {
        if(current_char == '"')
        {
            inside_quotation = not inside_quotation;
        }
        else if(current_char == delimiter and not inside_quotation)
        {
            result.push_back("");
        }
        else
        {
            result.back().push_back(current_char);
        }
    }
    if(result.back() == "")
    {
        result.erase(--result.end());
    }
    return result;
}

// Funktio lukee käyttäjän antamalla nimellä tiedoston ja
// tallentaa sen rivit stringinä vektoriin.

bool read_input_file(const string& filename, vector <string>& rivit) {
    ifstream input_file_in(filename);
    if (not input_file_in) {
        return false;
    }
    string line;
    while (getline(input_file_in,line)) {
        rivit.push_back(line);
    }
    return true;
}

// Funktio tarkistaa onko luetun tiedoston tietueet
// käyttökelpoisia

bool validate_fields(const vector<string>& fields) {
    if (fields.size() != 4) {
        return false;
    }
    for (const auto& field : fields) {
        if (field.empty()) {
            return false;
        }
    }
    return true;
}

// Funktio erottelee tiedostosta luettujen rivien tiedot ja tallentaa ne
// tietorakenteeseen map<string,vector<Course>>myöhempää käsittelyä varten

bool parse_input_line (const vector<string>& rivit,
                       map<string,vector<Course>>& kurssi_kirjasto) {
    for (const string& line : rivit) {
        vector<string> tietueet = split_ignoring_quoted_delim(line,DELIMETER);

        if (!validate_fields(tietueet)) {
            return false;
        }

        const string& teema = tietueet.at(0);
        const string& nimi = tietueet.at(1);
        const string& sijainti = tietueet.at(2);
        int osallistujat = 0;
        if (tietueet.at(3) == "full") {
            osallistujat = COURSE_FULL;
        }
        else {
            istringstream osallistujia_kursissa(tietueet.at(3));
            osallistujia_kursissa >> osallistujat;
            if (!osallistujia_kursissa >> osallistujat) {
                return false;
            }
        }

        Course uusi_kurssi = Course{nimi,sijainti,osallistujat};
        vector<Course>& kurssi_teemalla = kurssi_kirjasto[teema];
        auto it = kurssi_teemalla.begin();

        for (; it != kurssi_teemalla.end();it++) {
            if (it->nimi == uusi_kurssi.nimi && it->sijainti == uusi_kurssi.sijainti) {
                break;
            }
        }
        if (it != kurssi_teemalla.end()) {
            kurssi_teemalla.erase(it);
        }
        kurssi_teemalla.push_back(uusi_kurssi);
    }
    return true;
}

// Tämä funktio tarkistaa onko käyttäjän antama teema olemassa

bool tarkista_teema(map<string,vector<Course>>& kurssi_kirjasto, string teema) {
    for (const pair<string,vector<Course>> pari : kurssi_kirjasto) {
        if (teema == pari.first) {
            return true;
        }
    }
    return false;
}

// Tämä funktio tarkistaa onko käyttäjän antama paikkakunta olemassa

bool tarkista_sijainti(const map<string,vector<Course>>& kurssi_kirjasto,
                       string paikkakunta) {
    for (pair<string,vector<Course>> pari : kurssi_kirjasto) {
        for (const Course& kurssi : pari.second) {
            if (kurssi.sijainti == paikkakunta) {
                return true;
            }
        }
    }
    return false;
}

// Tämä funktio tarkistaa onko käyttäjän antamaa kurssia olemassa

bool tarkista_nimi(const map<string,vector<Course>>& kurssi_kirjasto,
                       string nimi) {
    for (pair<string,vector<Course>> pari : kurssi_kirjasto) {
        for (const Course& kurssi : pari.second) {
            if (kurssi.nimi == nimi) {
                return true;
            }
        }
    }
    return false;
}

// Funktio tulostaa tietorakenteeseen tallennetut teemat
// aakkosjärjestyksessä

void print_themes(map<string,vector<Course>>& kurssit_teemoittain) {
    set<string> teemat_aakkosittain;
    // Tallennetaan teemat set rakenteeseen jotta ne voidaan tulostaa
    // aakkosjärjestyksessä
    for (pair<string,vector<Course>> kurssi : kurssit_teemoittain) {
        teemat_aakkosittain.insert(kurssi.first);
    }
    for (auto& teema : teemat_aakkosittain) {
        cout << teema << endl;
    }
}

//Fukntio tulostaa käyttäjän antaman paikan ja teeman perusteella
//saatavilla olevat kurssit
void print_courses(map<string,vector<Course>>& kurssit_teemoittain,
                   string paikkakunta,
                   string teema) {

    if (!tarkista_teema(kurssit_teemoittain,teema)) {
        cout << "Error: unknown theme" << endl;
        return;
    }
    if (!tarkista_sijainti(kurssit_teemoittain,paikkakunta)) {
        cout << "Error: unknown location" << endl;
        return;
    }
    // Tallennetaan kurssien tiedot map tietorakenteeseen
    // jotta ne saadaan aakkosjärjestykseen
    map<string,int> nimi_aakkosittain;
    for (pair<string,vector<Course>> kurssi_pari : kurssit_teemoittain) {
        for (Course& kurssi : kurssi_pari.second) {
            if (teema == kurssi_pari.first and paikkakunta == kurssi.sijainti) {
                nimi_aakkosittain.insert({kurssi.nimi,kurssi.osallistujat});
            }
        }
    }
    // tulostetaan kurssien tiedot äsken muodostetusta tietorakenteesta
    for (pair<string,int> printtaukseen : nimi_aakkosittain) {
        cout << printtaukseen.first;
        if (printtaukseen.second == 50) {
            cout << " --- " << "full" << endl;
        }
        else {
            cout << " --- " << printtaukseen.second << " enrollments" << endl;
        }
    }
}

// Funktio tulostaa kurssien tiedot joissa on vielä tilaa

void print_available(map<string,vector<Course>>& kurssit_teemoittain) {

    // Tallennetaan kurssien tiedot tietorakenteeseen niiden
    // oikeassa järjestyksessä tulostamista varten
    map<string,map<string,set<string>>> teemat_aakkosittain;
    for (pair<string,vector<Course>> kurssi_pari : kurssit_teemoittain) {
        map<string,set<string>> apu_map;
        for (Course& kurssi : kurssi_pari.second) {
            if (kurssi.osallistujat != 50) {
                if (apu_map.find(kurssi.sijainti) != apu_map.end()) {
                    apu_map.at(kurssi.sijainti).insert(kurssi.nimi);
                } else {
                    apu_map.insert({kurssi.sijainti,{kurssi.nimi}});
                }
            }
        }
        teemat_aakkosittain.insert({kurssi_pari.first,apu_map});
    }

    for (pair<string,map<string,set<string>>> pari_1 : teemat_aakkosittain) {
        for (pair<string,set<string>> pari_2 : pari_1.second) {
            for (auto& nimi : pari_2.second) {
                cout << pari_1.first << " : "
                     << pari_2.first << " : "
                     << nimi
                     << endl;
            }
        }
    }
}

// Funktio tulostaa tietyn teeman kaikki kurssit

void print_courses_in_theme(map<string,vector<Course>>& kurssit_teemoittain,
                            string teema) {

    if (!tarkista_teema(kurssit_teemoittain,teema)) {
        cout << "Error: unknown theme" << endl;
        return;
    }
    map<string,vector<string>> sijainnit_aakkosittain;
    for (Course& kurssi : kurssit_teemoittain.at(teema)) {
            if (sijainnit_aakkosittain.find(kurssi.sijainti) != sijainnit_aakkosittain.end()) {
                sijainnit_aakkosittain.at(kurssi.sijainti).push_back(kurssi.nimi);
            } else {
                sijainnit_aakkosittain.insert({kurssi.sijainti,{kurssi.nimi}});
            }
        }
    for (pair<string,vector<string>> printtaukseen : sijainnit_aakkosittain) {
        for (string& nimi : printtaukseen.second) {
            cout << printtaukseen.first << " : "
                 << nimi
                 << endl;
        }
    }
}

// Funktio tulostaa tietyllä paikkakunnalla sijaitsevat kurssit

void print_courses_in_location(map<string,vector<Course>>& kurssit_teemoittain,
                               string paikkakunta) {

    if (!tarkista_sijainti(kurssit_teemoittain,paikkakunta)) {
        cout << "Error: unknown location" << endl;
        return;
    }
    set<string> nimet_aakkosittain;
    for (pair<string,vector<Course>> kurssi_vektori : kurssit_teemoittain) {
        for (Course& kurssi : kurssi_vektori.second) {
            if (kurssi.sijainti == paikkakunta) {
                nimet_aakkosittain.insert(kurssi.nimi);
            }
        }
    }
    for (auto& nimi : nimet_aakkosittain) {
        cout << nimi << endl;
    }
}

// Funktio laskee suosituimman teeman/teemat osallistujamäärän mukaan ja
// tulostaa sen tiedot

void print_favorite_theme(map<string,vector<Course>>& kurssit_teemoittain) {

    if (size(kurssit_teemoittain) == 0) {
        cout << "No enrollments" << endl;
        return;
    }
    int suosituin_luku = 0;
    int nykyinen_luku = 0;
    set<string> suosituin_teema;
    // Lasketaan jokaisen teeman kokonaisosallistujamäärä ja tallennetaan
    // suurin luku myöhempää käyttöä varten
    for (pair<string,vector<Course>> kurssi_pari : kurssit_teemoittain) {
        for (Course& kurssi : kurssi_pari.second) {
            nykyinen_luku += kurssi.osallistujat;
        }
        suosituin_luku = max(suosituin_luku,nykyinen_luku);
        nykyinen_luku = 0;
    }
    // Tähän olisi varmasti jokin järkevämpi ratkaisu mutta
    // osallistujamäärät lasketaan uudestaan ja tallennetaan millä
    // teemoilla on suurin_luku määrä osallistujia
    for (pair<string,vector<Course>> kurssi_pari : kurssit_teemoittain) {
        for (Course& kurssi : kurssi_pari.second) {
            nykyinen_luku += kurssi.osallistujat;
        }
        if (nykyinen_luku == suosituin_luku) {
            suosituin_teema.insert(kurssi_pari.first);
        }
        nykyinen_luku = 0;
    }
    // Tulostetaan osallistujamäärä ja suosituimmat teemat
    cout << suosituin_luku << " enrollments in themes" << endl;
    for (auto& teema : suosituin_teema) {
        cout << "--- " << teema << endl;
    }
}

// Tämä funktio poistaa käyttäjän antaman nimiset kurssit kaikkialta tietokannasta

void cancel(map<string,vector<Course>>& kurssit_teemoittain,string kurssin_nimi) {

    if (!tarkista_nimi(kurssit_teemoittain,kurssin_nimi)) {
        cout << "Error: unknown course" << endl;
        return;
    }
    vector<int> kurssit;
    // Tarkistetaan jokaisesta teemasta onko siinä annetun nimisiä kursseja. Jos
    // kursseja löytyy Course vektorista poistetaan yksi kerrallan kurssit
    // kunnes niitä ei enää löydetä
    for (pair<string,vector<Course>> kurssi_pari : kurssit_teemoittain) {
            for (Course& kurssi : kurssi_pari.second) {
                vector<Course>::iterator it = kurssit_teemoittain.at(kurssi_pari.first).begin();
                if (kurssi.nimi == kurssin_nimi) {
                    while (it != kurssit_teemoittain.at(kurssi_pari.first).end()) {
                        if (it->nimi == kurssin_nimi) {
                            kurssit_teemoittain.at(kurssi_pari.first).erase(it);
                            break;
                        }
                        ++it;
                }
            }
        }
    }
    cout << kurssin_nimi << " cancelled in all locations" << endl;
}

// Mainissa on toteutettu tiedoston lukuun vaadittavat funktiokutsut
// sekä käyttöliittymä

int main()
{
    string filename;
    cout << "Input file: ";
    getline(cin, filename);

    vector <string> tiedoston_rivit;
    if (!read_input_file(filename,tiedoston_rivit)) {
        cout << "Error: the input file cannot be opened" << endl;
        return EXIT_FAILURE;
    }

    map<string,vector<Course>> kurssit_teemoittain;
    if (!parse_input_line(tiedoston_rivit,kurssit_teemoittain)) {
        cerr << "Error: empty field" << endl;
        return EXIT_FAILURE;
    }

    while (true) {
        string rivi;
        cout << "> ";
        getline(cin,rivi);
        vector<string> osat = split_ignoring_quoted_delim(rivi, ' ');
        string komento = osat.at(0);

        if (komento == "themes") {
            print_themes(kurssit_teemoittain);
        }

        else if (komento == "courses") {
            //<paikkakuta><teema>
            if (size(osat) <= 2 or size(osat) >= 4) {
                cout << "Error: error in command courses" << endl;
                continue;
            }
            print_courses(kurssit_teemoittain,osat.at(1),osat.at(2));
        }

        else if (komento == "available") {
            print_available(kurssit_teemoittain);
        }

        else if (komento == "courses_in_theme") {
            //<teema>
            if (size(osat) < 2) {
                cout << "Error: error in command courses_in_theme" << endl;
                continue;
            }
            print_courses_in_theme(kurssit_teemoittain,osat.at(1));
        }

        else if (komento == "courses_in_location") {
            //<paikkakunta>
            if (size(osat) < 2) {
                cout << "Error: error in command courses_in_location" << endl;
                continue;
            }
            print_courses_in_location(kurssit_teemoittain,osat.at(1));
        }

        else if (komento == "favorite_theme") {
            print_favorite_theme(kurssit_teemoittain);
        }

        else if (komento == "cancel") {
            //<kurssi>
            cancel(kurssit_teemoittain,osat.at(1));
        }

        else if (komento == "quit") {
            return EXIT_SUCCESS;
        }
        else {
            cout << "Error: Unknown command: " << komento << endl;
        }
    }
}
