#include "mainwindow.hh"
#include "ui_mainwindow.h"
#include "gameboard.hh"
#include "square.hh"


// Couple of constants for testing
// BOARD_SIZE must be the same as in class GameBoard for
// the code to work
int SEED = 5545523;
int BOARD_SIZE = 10;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);    
    board_.giveNewSize(BOARD_SIZE);
    initButtons(BOARD_SIZE);
    initMenu();
    timer_ = new QTimer(this);
    connect(timer_, &QTimer::timeout, this, &MainWindow::onSecTimer);
}

MainWindow::~MainWindow() {
    delete ui;
}

// Locates the button player has pressed
void MainWindow::findButton() {

    int x = 0;
    int y = 0;
    for (std::vector<QPushButton*>& button_vector : buttons_) {
        ++x;
        y = 0;
        for (QPushButton* button : button_vector) {
            ++y;
            if (button == sender()) {
                handleClick(x,y);
            }
        }
    }
}

// Creates buttons through which player can interact with
// GameBoard class
void MainWindow::initButtons(int board_size) {

    QWidget* central = new QWidget(this);
    QGridLayout* grid_layout = new QGridLayout(central);

    for (int x = 0; x < board_size ; ++x) {
        std::vector<QPushButton*> button_vector;
        button_vector.clear();
        for (int y = 0; y < board_size ; ++y) {
            // creates new button gives it correct properties
            QPushButton* push_button = new QPushButton(this);
            push_button->setFixedHeight(50);
            push_button->setFixedWidth(50);
            button_vector.push_back(push_button);

            grid_layout->addWidget(push_button, x, y);

            connect(push_button, &QPushButton::clicked, this, &MainWindow::findButton);
        }
        buttons_.push_back(button_vector);
    }
    // valgrind memory analysis doesn't spot this warning so
    // maybe this is qt creators bug
    setCentralWidget(central);
    disableButtons();
}

// Creates new game by initiating new board in
// class GameBoard and enables game buttons to be used
void MainWindow::initGame() {
    int seed = getSeed();
    time_counter_->display(0);
    enableButtons();
    board_.resetBoard();
    board_.init(seed);
    updateGui();
}

// Generater menu in top side of gui.
// Menu allows player to change settings of the game
void MainWindow::initMenu() {

    // creates new layout and individual buttons
    QWidget* menu = new QWidget(this);
    QHBoxLayout* menu_layout = new QHBoxLayout(menu);

    flag_toggle_ = new QPushButton("Open",this);
    flag_toggle_->setMaximumWidth(96);
    connect(flag_toggle_, &QPushButton::clicked, this, &MainWindow::setFlag);

    seed_input_ = new QLineEdit("<give seed here>",this);
    seed_input_->setMaximumHeight(30);
    seed_input_->setMaximumWidth(120);

    generate_board_ = new QPushButton("Generate", this);
    generate_board_->setMaximumWidth(120);
    connect(generate_board_, &QPushButton::clicked, this, &MainWindow::initGame);
    connect(generate_board_, &QPushButton::clicked, this, &MainWindow::startTimer);

    check_flags_ = new QPushButton("Check flags",this);
    check_flags_->setMaximumWidth(120);
    connect(check_flags_, &QPushButton::clicked, this, &MainWindow::checkFlags);

    time_counter_ = new QLCDNumber(this);
    time_counter_->setMaximumWidth(60);

    // add widgets in to layout
    menu_layout->addWidget(flag_toggle_);
    menu_layout->addWidget(generate_board_);
    menu_layout->addWidget(check_flags_);
    menu_layout->addWidget(seed_input_);
    menu_layout->addWidget(time_counter_);

    setMenuWidget(menu);
}

// Handles game logig of the button player chooses
void MainWindow::handleClick(int x, int y) {

    Square square = board_.getSquare(x-1,y-1);
    // checks every possible interaction with square
    // and passes it on to GameBoard class
    if(square.hasFlag()) {
        if(set_flag_) {
            square.removeFlag();
        }
    }
    else if(not set_flag_) {
        square.open();
    }
    else {
        square.addFlag();
    }
     board_.setSquare(square, x - 1, y - 1);
     if (board_.isGameOver()) {
         disableButtons();
         stopTimer();
         seed_input_->setText("You won!");
     }
     updateGui();
}

// Handles if player is setting a flag or opening a square by
// giving true or false to set_flag_
void MainWindow::setFlag() {

    ++flag_counter_;
    if (flag_counter_ % 2 == 0) {
        set_flag_ = true;
        flag_toggle_->setText("Flag");
    }
    else if (flag_counter_ % 2 == 1) {
        set_flag_ = false;
        flag_toggle_->setText("Open");
    }
}

// Updates correct marks on game buttons
void MainWindow::updateGui() {
    // goes through every button and corresponding square
    int x = 0;
    int y = 0;
    for (std::vector<QPushButton*>& button_vector : buttons_) {
        ++x;
        y = 0;
        for (QPushButton* button : button_vector) {
            ++y;
            Square square = board_.getSquare(x-1,y-1);
            // checks every possible mark for current square
            if (not square.isOpen()) {
                button->setText("");
            }
            else if (square.isOpen()) {
                if (square.hasMine()) {
                    button->setText("M");
                    seed_input_->setText("BOOM! you lost");
                    stopTimer();
                    disableButtons();
                    findMines();
                }
                else if (not square.hasMine()) {
                    QString mine_count = QString::number(square.countAdjacent());
                    button->setText(mine_count);
                }
            }            
            if (square.hasFlag()) {
                button->setText("F");
            }
        }
    }
}

// Hadles timers signal and updates guis time counter
void MainWindow::onSecTimer() {
    int seconds = time_counter_->intValue();
    ++seconds;
    time_counter_->display(seconds);
}

// Checks if the flags are on mines
void MainWindow::checkFlags() {

    // settin up palettes
    QBrush red_brush(Qt::red);
    QPalette red_palette;
    red_palette.setBrush(QPalette::Button, red_brush);

    QBrush green_brush(Qt::green);
    QPalette green_palette;
    green_palette.setBrush(QPalette::Button, green_brush);

    // checks every mine checks flags and mines
    for (int x = 1 ; x <= BOARD_SIZE ; ++x) {
        for (int y = 1 ; y <= BOARD_SIZE ; ++y) {
            Square square = board_.getSquare(x-1, y-1);

            if (square.hasFlag() and not square.hasMine()) {
                check_flags_->setPalette(red_palette);
                return;
            }
            else {
                check_flags_->setPalette(green_palette);
            }
        }
    }
}

// Starts the timer
void MainWindow::startTimer() {
    timer_->start(1000);
}

// Stops the timer
void MainWindow::stopTimer() {
    timer_->stop();
}

// Reads the seed player has given and
// checks if its viable
int MainWindow::getSeed() {

    QString seed_q = seed_input_->text();
    std::string seed_str = seed_q.toStdString();
    // checks if the seed is viable for use
    for (char mark : seed_str) {
        if (isalpha(mark)) {
            seed_input_->setText("Only numbers!");
            return time(NULL);
        }
    }
    int seed_int = std::stoi(seed_str);
    return seed_int;

}

// Enables buttons used in game
void MainWindow::enableButtons() {
    for (std::vector<QPushButton*>& button_vector : buttons_) {
        for (QPushButton* button : button_vector) {
            button->setEnabled(true);
        }
    }
}

// Disables buttons used in game
void MainWindow::disableButtons() {
    for (std::vector<QPushButton*>& button_vector : buttons_) {
        for (QPushButton* button : button_vector) {
            button->setDisabled(true);
        }
    }
}

// Locates every mine in gameboard and places M on corresponding buttons
void MainWindow::findMines() {

    int x = 0;
    int y = 0;
    for (std::vector<QPushButton*>& button_vector : buttons_) {
        ++x;
        y = 0;
        for (QPushButton* button : button_vector) {
            ++y;
            Square square = board_.getSquare(x-1,y-1);
            if (square.hasMine()) {
                square.open();
                button->setText("M");
                board_.setSquare(square,x-1,y-1);
            }
        }
    }
}




