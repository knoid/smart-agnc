#ifndef COMMANDS_H_
#define COMMANDS_H_

int cmd_exit(agnHandle_t handle, int argc, char *argv[]);

int cmd_action_connect(agnHandle_t handle, int argc, char *argv[]);

int cmd_action_disconnect(agnHandle_t handle, int argc, char *argv[]);

int cmd_get_connect_attempt_info(agnHandle_t handle, int argc, char *argv[]);

int cmd_get_state(agnHandle_t handle, int argc, char *argv[]);

int cmd_get_user_info(agnHandle_t handle, int argc, char *argv[]);

typedef int (*cmd_function_t)(agnHandle_t, int, char**);

#endif /* COMMANDS_H_ */
