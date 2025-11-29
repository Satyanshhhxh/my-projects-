#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <conio.h>
#include <windows.h>

#define WIDTH 80
#define HEIGHT 24
#define PADDLE_WIDTH 20
#define PADDLE_Y (HEIGHT - 2)
#define MAX_OBSTICLE 10        
#define framerate  55       
#define BALL_CHAR 'O'
#define PADDLE_CHAR '____'
#define BORDER_CHAR '#'
#define OBST '/'       
#define OBSTB '\\'    
#define PADDLE_SPEED 16

char screen[HEIGHT][WIDTH + 1]; 

typedef struct {
    int x, y;
    char type;
} Obstacle;

Obstacle obstacles[MAX_OBSTICLE];
int obs_count = 0;

void gotoxy(int x, int y) {
    COORD c = { (SHORT)x, (SHORT)y };
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), c);
}

void hideCursor() {
    CONSOLE_CURSOR_INFO ci;
    ci.bVisible = FALSE;
    ci.dwSize = 1;
    SetConsoleCursorInfo(GetStdHandle(STD_OUTPUT_HANDLE), &ci);
}

void clear_screen_buffer() {
    for (int r = 0; r < HEIGHT; ++r) {
        for (int c = 0; c < WIDTH; ++c) screen[r][c] = ' ';
        screen[r][WIDTH] = '\0';
    }
}

void draw_border_buffer() {
    for (int x = 0; x < WIDTH; ++x) {
        screen[0][x] = BORDER_CHAR;
        screen[HEIGHT - 1][x] = BORDER_CHAR;
    }
    for (int y = 0; y < HEIGHT; ++y) {
        screen[y][0] = BORDER_CHAR;
        screen[y][WIDTH - 1] = BORDER_CHAR;
    }
}

void draw_obstacles_buffer() {
    for (int i = 0; i < obs_count; ++i) {
        int x = obstacles[i].x;
        int y = obstacles[i].y;
        if (x > 0 && x < WIDTH-1 && y > 0 && y < HEIGHT-1)
            screen[y][x] = obstacles[i].type;
    }
}

void render_buffer() {
    gotoxy(0, 0);
    for (int r = 0; r < HEIGHT; ++r) {
        printf("%s\n", screen[r]);
    }
}

void draw_paddle_buffer(int paddle_x) {
    if (paddle_x < 1) paddle_x = 1;
    if (paddle_x > WIDTH - PADDLE_WIDTH - 1) paddle_x = WIDTH - PADDLE_WIDTH - 1;
    for (int i = 0; i < PADDLE_WIDTH; ++i) {
        int px = paddle_x + i;
        if (px > 0 && px < WIDTH - 1)
            screen[PADDLE_Y][px] = PADDLE_CHAR;
    }
}

void draw_ball_buffer(int bx, int by) {
    if (bx > 0 && bx < WIDTH-1 && by > 0 && by < HEIGHT-1)
        screen[by][bx] = BALL_CHAR;
}

void init_obstacles_random() {
    obs_count = MAX_OBSTICLE;
    for (int i = 0; i < obs_count; ++i) {
        int x, y;
        do {
            x = 2 + rand() % (WIDTH - 6);
            y = 2 + rand() % (HEIGHT - 8);
        } while (y >= PADDLE_Y - 3); 
        obstacles[i].x = x;
        obstacles[i].y = y;
        obstacles[i].type = (rand() % 2) ? OBST : OBSTB;
    }
}

void reflect_on_obstacle(int *dx, int *dy, char type) {
    int ndx = *dx;
    int ndy = *dy;
    if (type == OBST) {
        ndx = -(*dy);
        ndy = -(*dx);
    } else { 
        ndx = (*dy);
        ndy = (*dx);
    }
    if (ndx > 1) ndx = 1; if (ndx < -1) ndx = -1;
    if (ndy > 1) ndy = 1; if (ndy < -1) ndy = -1;
    if (ndx == 0 && ndy == 0) ndy = 1;
    *dx = ndx;
    *dy = ndy;
}

int main(void) {
    srand((unsigned)time(NULL));
    hideCursor();

    int paddle_x = (WIDTH - PADDLE_WIDTH) / 2;
    int ball_x = WIDTH / 2;
    int ball_y = HEIGHT / 4;
    int ball_dx = 1;
    int ball_dy = 1; 
    int score = 0;
    int lives = 3;

    init_obstacles_random();

    system("cls");
    printf("Advanced Paddle Game (mixed diagonal obstacles)\n\n");
    printf("Controls: A = left, D = right, Q = quit\n");
    printf("Faster paddle + smoother frames. Score increases on each paddle hit.\n");
    printf("Press any key to start...");
    _getch();

    while (1) {
        clear_screen_buffer();
        draw_border_buffer();
        draw_obstacles_buffer();

        draw_paddle_buffer(paddle_x);
        draw_ball_buffer(ball_x, ball_y);

        char hud[64];
        snprintf(hud, sizeof(hud), " Score: %d   Lives: %d ", score, lives);
        for (int i = 0; hud[i] != '\0' && i < WIDTH-4; ++i) {
            screen[0][2 + i] = hud[i];
        }

        render_buffer();

        if (_kbhit()) {
            int ch = _getch();
            if (ch == 'a' || ch == 'A') {
                paddle_x -= PADDLE_SPEED;
                if (paddle_x < 1) paddle_x = 1;
            } else if (ch == 'd' || ch == 'D') {
                paddle_x += PADDLE_SPEED;
                if (paddle_x > WIDTH - PADDLE_WIDTH - 1) paddle_x = WIDTH - PADDLE_WIDTH - 1;
            } else if (ch == 'q' || ch == 'Q') {
                break; 
            }
        }

        int next_x = ball_x + ball_dx;
        int next_y = ball_y + ball_dy;

        if (next_x <= 1) {
            ball_dx = abs(ball_dx); 
            next_x = ball_x + ball_dx;
        } else if (next_x >= WIDTH - 2) {
            ball_dx = -abs(ball_dx); 
            next_x = ball_x + ball_dx;
        }

        if (next_y <= 1) {
            ball_dy = abs(ball_dy); 
            next_y = ball_y + ball_dy;
        }

        if (next_y == PADDLE_Y - 1) {
            if (next_x >= paddle_x && next_x <= paddle_x + PADDLE_WIDTH - 1) {
                ball_dy = -abs(ball_dy);

                int center = paddle_x + PADDLE_WIDTH / 2;
                if (next_x < center) ball_dx = -1;
                else if (next_x > center) ball_dx = 1;
                else ball_dx = 0;

                score++; 
            }
        }

        for (int i = 0; i < obs_count; ++i) {
            if (obstacles[i].x == next_x && obstacles[i].y == next_y) {
                reflect_on_obstacle(&ball_dx, &ball_dy, obstacles[i].type);
                next_x = ball_x + ball_dx;
                next_y = ball_y + ball_dy;
                break;
            }
        }

        ball_x = next_x;
        ball_y = next_y;

        if (ball_y >= HEIGHT - 1) {
            lives--;
            if (lives <= 0) {
                clear_screen_buffer();
                draw_border_buffer();
                render_buffer();
                gotoxy(WIDTH/2 - 10, HEIGHT/2);
                printf("GAME OVER! Final Score: %d\n", score);
                gotoxy(0, HEIGHT);
                break;
            } else {
                ball_x = WIDTH / 2;
                ball_y = HEIGHT / 2;
                ball_dx = (rand()%2) ? 1 : -1;
                ball_dy = -1;
                paddle_x = (WIDTH - PADDLE_WIDTH) / 2;
                Sleep(600);
            }
        }

        Sleep(framerate );
    }

    return 0;
}
