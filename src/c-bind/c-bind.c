#include <agnc.h>
#include <agnLogc.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <poll.h>
#include <sys/time.h>

#include "commands.h"

#define MAX_COMMANDS 6

int state_change_callback(int parameter) {
    printf("state_change\t%d\n", parameter);
    return EXIT_SUCCESS;
}

int action_requested_callback(int parameter) {
    printf("action_requested\t%d\n", parameter);
    return EXIT_SUCCESS;
}

const cmd_function_t cmd_functions[MAX_COMMANDS] = {
    cmd_exit,
    cmd_action_connect,
    cmd_action_disconnect,
    cmd_get_connect_attempt_info,
    cmd_get_state,
    cmd_get_user_info
};

int main(int argc, char *argv[]) {
    setbuf(stdout, NULL);

    agnHandle_t handle;

    int poll_ret;
    struct pollfd fd;

    char *line, *char_nargs;
    size_t nbytes = 100;
    int commandId, nargs, i;
    char **args;
    ssize_t bytes_read;

    agnLogcOpen(AGN_LOG_ID_GENERIC);
    agnLogcLevel(AGN_LOG_DEBUG);

    handle = agncOpen(agnComponentIdAGNClient,
    state_change_callback, action_requested_callback);

    for (;;) {

        // Needs to be set in every loop because `poll` may modify it.
        fd.fd = 0;
        fd.events = POLLIN;
        fd.revents = 0;

        commandId = nargs = -1;

        // wait for input on stdin until timeout
        poll_ret = poll(&fd, 1, 500);

        // read input
        if (poll_ret > 0 && (fd.revents & POLLIN != 0)) {
            line = NULL;
            bytes_read = getline(&line, &nbytes, stdin);
            if (bytes_read > 3) { // number + space + number + line break = 4
                commandId = strtol(strtok(line, " "), NULL, 10);
                char_nargs = strtok(NULL, " ");
                if (char_nargs != NULL) {
                    nargs = strtol(char_nargs, NULL, 10);
                }
            }
            free(line);
        }

        // check valid input
        if (-1 < commandId && commandId < MAX_COMMANDS && nargs >= 0) {

            args = (char**) malloc(sizeof(char*) * nargs);
            for (i = 0; i < nargs; i++) {
                line = NULL;
                bytes_read = getline(&line, &nbytes, stdin);

                // remove trailing line end
                args[i] = (char*) malloc(sizeof(char) * bytes_read);
                line[bytes_read - 1] = '\0';
                strcpy(args[i], line);

                free(line);
            }

            if (cmd_functions[commandId](handle, nargs, args) == EXIT_FAILURE) {
                break;
            }

            for (i = 0; i < nargs; i++) {
                free(args[i]);
            }
            free(args);

        } else if (poll_ret > 0) {
            fprintf(stderr, "Invalid command\n");
            break;
        }
    }

    agncClose(handle);

    return EXIT_SUCCESS;
}
