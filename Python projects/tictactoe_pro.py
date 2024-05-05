"""
COMP.CS.100 Ohjelmointi 1 / Programming 1

Ristinollapeli joka koostuu valikko ikkunasta sekä peli-ikkunasta. Aktivoimalla MenuWindowin
avautuu valikko josta voi valita mieleisen pelikentän. Kun kenttä on valittu start nappi luo
uuden ikkunan, missä on valitun kokoinen ristinollapeli. Pelin päätyttyä ohjelma avaa valikkoikkunan ja
näyttää miten edellinen peli päättyi. Tähtään kehittyneeseen versioon projektista.
"""

from tkinter import *


class MenuWindow:

    def __init__(self, winner=0):
        """
        Luo suurimman osan napeista  ja tekstikentistä aloitusnäyttöön
        :param winner: Pelin jälkeen näytössä näkyy kumpi pelaaja voitti pelin
                       ja tämä parametri on sen selvittämistä varten.
        """

        self.__menuwindow = Tk()
        self.__choice = IntVar()
        self.__choice.set(1)
        menu = self.__menuwindow

        # atribuutti joka tarkistaa voiko custom gamen kenttiä luoda
        self.__allow_creation = True

        # Valmiiksi määriteltyjä peliruudukoita
        self.__firstchoice = Radiobutton(
                                         menu,
                                         text="3x3, 3 in row",
                                         variable=self.__choice,
                                         value=1,
                                         command=self.destroy_entrys
                                        )

        self.__secondchoice = Radiobutton(
                                          menu,
                                          text="8x8, 4 in row",
                                          variable=self.__choice,
                                          value=2,
                                          command=self.destroy_entrys
                                         )

        self.__customgrid = Radiobutton(
                                        menu,
                                        text="custom grid",
                                        variable=self.__choice,
                                        value=3,
                                        command=self.custom_game
                                       )

        self.__start = Button(menu,
                              text="Start game!",
                              command=self.create_game)
        self.__quit = Button(menu,
                             text="Exit",
                             command=self.exit)

        self.__text1 = Label(menu, text="Welcome to tic tac toe!")
        self.__text2 = Label(menu, text="Choose a grid.")
        self.__win_label = Label(menu, text=f"player {winner} wins!")
        self.__tielabel = Label(menu, text="Its a tie!")

        # Paikat napeille
        self.__firstchoice.grid(row=2, column=0)
        self.__secondchoice.grid(row=3, column=0)
        self.__customgrid.grid(row=4, column=0)
        self.__text1.grid(row=0, column=0)
        self.__text2.grid(row=1, column=0)
        self.__start.grid(row=5, column=0)
        self.__quit.grid(row=6, column=0)
        # Tämä nappi tulee näkyviin vasta kun peli on pelattu
        if winner != 0:
            if winner == 3:
                self.__tielabel.grid(row=3, column=2)
            else:
                self.__win_label.grid(row=3, column=2)

        menu.mainloop()

    def custom_game(self):
        """
        Luo entry kentät ja tekstit custom gamea varten jos
        allow_creation sallii sen
        :return: ei paluuarvoa
        """

        if self.__allow_creation:
            self.__width_value = Entry()
            self.__height_value = Entry()
            self.__win_condition = Entry()

            self.__heightlabel = Label(self.__menuwindow,
                                       text="height")
            self.__widthlabel = Label(self.__menuwindow,
                                      text="width")
            self.__winlabel = Label(self.__menuwindow,
                                    text="x in row to win")

            self.__height_value.grid(row=5, column=1)
            self.__width_value.grid(row=6, column=1)
            self.__win_condition.grid(row=7, column=1)
            self.__heightlabel.grid(row=5, column=0)
            self.__widthlabel.grid(row=6, column=0)
            self.__winlabel.grid(row=7, column=0)

            self.move_buttons(0)

        self.__allow_creation = False

    def destroy_entrys(self):
        """
        Tuhoaa ylimääräiset kentät selkeyden ja tyylikkyyden nimissä
        :return: ei paluuarvoa
        """

        try:
            self.__width_value.destroy()
            self.__height_value.destroy()
            self.__win_condition.destroy()
            self.__widthlabel.destroy()
            self.__heightlabel.destroy()
            self.__winlabel.destroy()
            # muuttaa menun tekstit alkuperäisiksi
            self.__text1.configure(text="Welcome to tic tac toe!")
            self.__text2.configure(text="Choose a grid.")
        # Jos kentät on jo olemassa tämä poistaa niiden uudelleen luomisesta
        # aiheutuvan virheen
        except AttributeError:
            pass

        self.__allow_creation = True

    def move_buttons(self, way):
        """
        siirtää start game ja exit nappeja kun
        custom game kenttiä luodaan
        :param way: suunta johon nappeja liikutetaan
        :return: ei paluuarvoa
        """

        if way == 0:
            self.__start.grid(row=8, column=0)
            self.__quit.grid(row=8, column=1)

        elif way == 1:
            self.__start.grid(row=5, column=0)
            self.__quit.grid(row=5, column=0)

    def check_input(self):
        """
        Tarkistaa käyttäjän antaman syöteen.
        Pituus ja leveys ei saa olla alle kolmen
        ja voitto pitää saada 3-6 suoran välillä
        :return: Palauttaa True tai False riippuen
        syöteen pätevyydestä
        """

        try:
            width = int(self.__width_value.get())
            height = int(self.__height_value.get())
            win = int(self.__win_condition.get())
        except ValueError:
            # Muuttaa tekstin tilalle käyttäjän virheellisen syötteen
            # tämä  on olemassa koska se on hauska mauste peliin
            conditions = [self.__width_value.get(), self.__height_value.get(), self.__win_condition.get()]
            for cond in conditions:
                if cond.isalpha():
                    self.__text1.configure(text="You fool!")
                    self.__text2.configure(text=f'"{cond}" is not number!')
            return False

        if width < 3 or width > 50:
            self.__text1.configure(text="Check your inputs.")
            self.__text2.configure(text="Width and height must between 3 and 50")
            return False
        if height < 3 or height > 50:
            self.__text1.configure(text="Check your inputs.")
            self.__text2.configure(text="Width and height must be between 3 and 50")
        if win < 3 or win > 6:
            self.__text1.configure(text="Check your inputs.")
            self.__text2.configure(text="Win condition must be between 3 and 6")
            return False

        return True

    def clear(self):
        """
        tyhjentää entry kentät virheellisen syötteen tapauksessa
        :return: ei paluuarvoa
        """
        self.__width_value.delete(0, END)
        self.__height_value.delete(0, END)
        self.__win_condition.delete(0, END)

    def exit(self):
        """sammuttaa pelin"""
        self.__menuwindow.destroy()

    def create_game(self):
        """
        Luo pelin jonka pelaaja valitsee. Jos valinta on 1 tai 2 luodaan valmis peli.
        Valinnalla 3 ohjelma tarkistaa pelaajan antamat syötteet
        ja luo niiden mukaisen pelin. Tämä funktio myös sammuttaa menu ikkunan.
        :return: Lopettaa funktion returnilla jos check_input antaa Falsen
        """
        if self.__choice.get() == 1:
            width  = 3
            height = 3
            win    = 3

        if self.__choice.get() == 2:
            width  = 8
            height = 8
            win    = 4
        # Luo pelin pelaajan annetuilla arvoilla
        elif self.__choice.get() == 3:
            if self.check_input():
                width = int(self.__width_value.get())
                height = int(self.__height_value.get())
                win = int(self.__win_condition.get())
            else:
                self.clear()
                return
        # Tuhoaa menu ikkunan pelin ajaksi
        self.exit()
        # Luo pelin aijemmin määritetyillä arvoilla
        TicTacToe(width, height, win)


class TicTacToe:

    def __init__(self, width, height, win):
        """
        Antaa alkuarvot tärkeille suureille. Luo pelikentän ja tallentaa napit, ja niitä vastaavat
        komennot matriiseihin joista niitä voi käsitellä kordinaattien avulla. Luo pohjan self.__marks
        matriisia varten johontallenetaan pelaajan asettamat merkit.
        :param width: Peliruudukon leveys
        :param height: Peliruudukon korkeus
        :param win: Voittoon tarvittava määrä merkkejä
        """

        self.__gamewindow = Tk()
        game = self.__gamewindow
        # alkuarvot tärkeille suureille joita tarvitaan
        # myöhemmin muissa funktioissa
        self.__turn = 1
        self.__placed_marks = 0
        self.__winning_row = win
        self.__width = width
        self.__height = height
        # Tekstit joista näkyy kummalla pelaajalla on X tai O
        self.__player1 = Label(game,
                               text="Player 1 [X]",
                               background="green"
                               )
        self.__player2 = Label(game,
                               text="Player 2 [O]",
                               background="blue",
                               foreground="white"
                               )
        # jos kentän leveys on alle kolme player tekstit jää tulostamatta
        # koskane näyttävät hassuilta 3x3 kentällä
        if width != 3:
            self.__player1.grid(row=height, column=0, columnspan=width // 2, sticky=W + E)
            self.__player2.grid(row=height, column=width // 2, columnspan=width // 2, sticky=W+E)

        self.__square = []
        self.__commands = []
        self.__marks = []
        # Luo matriisit tiedon varastoimista varten
        for _ in range(width):
            self.__square.append([None] * height)
            self.__commands.append([None] * height)
            self.__marks.append([None] * height)
        # Luo napit ja komennot joita vaaditaan pelin toimimiseen
        for y in range(height):
            for x in range(width):

                def button_press(x_coordinate=x, y_coordinate=y):
                    self.place_marker(x_coordinate, y_coordinate)

                self.__commands[x][y] = button_press

                new_button = Button(game,
                                    text="",
                                    width=4,
                                    heigh=2,
                                    command=button_press)

                new_button.grid(row=y, column=x)

                self.__square[x][y] = new_button

        game.mainloop()

    def place_marker(self, x, y):
        """
        Asettaa merkin X tai O pelikentälle ja tallentaa sen self.__marks matriisiin.
        Käynnistää voiton tarkastamisen ja tarkastuksen siitä onko pelikenttä täysi.
        :param x: Pelaajan painaman napin x-koordinaatti
        :param y: Pelaajan painaman napin y-koordinaatti
        :return: ei paluuarvoa
        """
        # luo muuttujan activated_button selvyyden vuoksi
        activated_button = self.__square[x][y]

        if self.__marks[x][y] is None:
            if self.__turn == 1:
                merkki = "X"
                self.__marks[x][y] = merkki
                self.__turn = 2
            else:
                merkki = "O"
                self.__marks[x][y] = merkki
                self.__turn = 1

            activated_button.configure(text=merkki)

            self.check_win()
            self.check_full()

    def check_win(self):
        """
        Tämä funktio tarkistaa onko pelaaja voittanut pelin. Lisähaastetta toi
        ei neliön muotoisten kenttien voiton tarkastaminen, joten funktio on erittäin
        pitkä ja ehkä hiukkasen spagettinen. Tarkastusmetodissa on ideana että funktio käy
        läpi arvoja kentän ylä- ja sivureunoilla, ja tarkistaa lähteekö niistä voittavia
        rivejä tiettyihin suuntiin. Funktio saattaa sisältää bugeja mutta lyhyehkön
        testailuni perusteella se toimi moitteettomasti.
        :return: ei paluuarvoa
        """
        # Nimetään muuttujat selvyyden vuoksi
        height = self.__height
        width = self.__width

        # Tarkistaa rivit yksitellen voittojen varalta
        # välillä x - width
        for x in range(0, width):

            y = 0
            check_counter = 1
            check = self.__marks[x][y]

            # Tarkistaa pystyrivit
            for n in range(1, height):
                next_in_row = self.__marks[x][n]
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

            # tarkistettava ruutu ja laskuri palautetaan alkuperäisiin
            # arvoihin jokaisen rivi tarkastelun välissä
            check = self.__marks[x][y]
            check_counter = 1

            # Tarkistaa Oikea ylä - vasen ala suunnassa /
            for n in range(1, height):
                try:
                    next_in_row = self.__marks[x - n][y + n]
                except IndexError:
                    break
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

            check = self.__marks[x][y]
            check_counter = 1

            # Tarkistaa vasen ylä - oikea ala suunnassa \
            for n in range(1, height):
                try:
                    next_in_row = self.__marks[x + n][y + n]
                except IndexError:
                    break
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

        # tarkastaa välillä y - height
        for y in range(0, height):

            x = 0
            check_counter = 1
            check = self.__marks[x][y]

            # Tarkistaa vaakarivit
            for n in range(1, width):
                try:
                    next_in_row = self.__marks[n][y]
                except IndexError:
                    break
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

            check = self.__marks[x][y]
            check_counter = 1

            # Tarkistaa Vasen ylä - oikee ala suunnassa \
            for n in range(1, width):
                try:
                    next_in_row = self.__marks[x + n][y + n]
                except IndexError:
                    break
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

            # vaihtaa x koordinaatiksi ruudukon vasemman laidan
            x = width - 1
            check = self.__marks[x][y]
            check_counter = 0

            # Tarkistaa oikea ylä - vasen ala suunnassa /
            for n in range(1, width):
                try:
                    next_in_row = self.__marks[x - n][y + n]
                except IndexError:
                    break
                if next_in_row is None or check != next_in_row:
                    check_counter = 1
                elif check == next_in_row:
                    check_counter += 1
                if check_counter == self.__winning_row:
                    self.win_ceremony()
                check = next_in_row

    def check_full(self):
        """
        Tarkistaa onko pelikenttä täynnä merkkejä.
        Jos se on peli loppuu ja molemmat häviää
        :return:
        """
        self.__placed_marks += 1
        square_count = self.__width * self.__height
        if self.__placed_marks == square_count:
            self.exit()
            MenuWindow(3)

    def exit(self):
        """sammuttaa käynnissä olevan pelin"""
        self.__gamewindow.destroy()

    def win_ceremony(self):
        """
        Funktio lopettaa pelin ja käynnistää menuikkunan missä
        lukee nyt pelin voittaja.
        :return: ei paluuarvoa
        """
        if self.__turn == 2:
            turn = 1
        else:
            turn = 2
        self.exit()
        MenuWindow(turn)


def main():

    MenuWindow()


if __name__ == "__main__":
    main()
