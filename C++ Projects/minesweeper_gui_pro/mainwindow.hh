/*Minesweeper
 * 
 *      
 * Description:
 *  This program implements game called minesweeper. The games goal is to
 *  find all of the mines and place flags on them to mark them out. When you click
 *  a square it gives information of how many mines there are in its adjacent squares.
 *  The game ends if you try to open a square that has mine in it or when you have
 *  succesfully out all mines with flags.
 *
 *  When starting the game squares are disabled. You can either enter seed for generating the game
 *  or let the computer generate seed. Game begins when you click generate button. Generate button
 *  can be pressed during any stage of the game and resets it. Player can choose between opening a square
 *  or placing a flag with a button in top left corner if the gui. The game also has timer
 *  which counts game time on seconds.
 *
 *  Symbols:
 *   - 1-8 means number of adjacent mines
 *   - M is Mine
 *   - F is flag
 *
 *  Possible bonus points:
 *   - switching between flag and open is made through pushButton, not radioButton
 *   - if unopened squares have mines, they are opened after the game ends
 *   - button for checking if current flags are placed correctly
 *
 * Structure and desing decisions:
 *  The progaram is divided in three classes. GameBoard and Square classes
 *  handle back end game logic. These classes were given to students and I only made
 *  minor modifications to them. Class MainWindow handles the front end of the program.
 *  Class MainWindow interacts with the other two classes and displays their
 *  information to user. More on the desing choices can be found in source code.
 *  Size of the board can be changed in mainwindow.cpp variable BOARD_SIZE
 *
 */

#ifndef MAINWINDOW_HH
#define MAINWINDOW_HH

#include <QRadioButton>
#include <QPushButton>
#include <QMainWindow>
#include <QLineEdit>
#include <QLCDNumber>
#include <QTimer>
#include <QSpinBox>
#include <cctype>
#include <string>
#include <vector>

#include "gameboard.hh"
#include "square.hh"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

public slots:
    void findButton();
    void initGame();
    void onSecTimer();
    void checkFlags();

private:
    Ui::MainWindow *ui;

    void initButtons(int board_size);
    void initMenu();
    void handleClick(int x, int y);
    void setFlag();
    void updateGui();
    void startTimer();
    void stopTimer();
    int getSeed();
    void enableButtons();
    void disableButtons();
    void findMines();

    std::vector<std::vector<QPushButton*>> buttons_;
    QLCDNumber* time_counter_;
    GameBoard board_;
    int flag_counter_ = 1;
    bool set_flag_ = false;
    QTimer* timer_;
    QLineEdit* seed_input_;
    QPushButton* check_flags_;
    QPushButton* generate_board_;
    QPushButton* flag_toggle_;

};
#endif // MAINWINDOW_HH
