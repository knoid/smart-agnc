#include <agnc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "commands.h"

void replace_newlines(char* text) {
    char* newLine = text;
    while (newLine = strchr(newLine, '\n')) {
        newLine[0] = '|';
    }
}

int cmd_exit(agnHandle_t handle, int argc, char *argv[]) {
    return EXIT_FAILURE;
}

int cmd_action_connect(agnHandle_t handle, int argc, char *argv[]) {
    agnUser_t user;

    user.ulStructSize = sizeof(agnUser_t);
    strcpy(user.szAccount, argv[0]);
    strcpy(user.szUsername, argv[1]);
    strcpy(user.szPassword, argv[2]);
    strcpy(user.szNewPassword, argv[3]);
    strcpy(user.szSMXServer, argv[4]);
    if (5 < argc) {
        strcpy(user.szProxyServer, argv[5]);
        strcpy(user.szProxyUser, argv[6]);
        strcpy(user.szProxyPassword, argv[7]);
    } else {
        strcpy(user.szProxyServer, "");
        strcpy(user.szProxyUser, "");
        strcpy(user.szProxyPassword, "");
    }

    agncPostActionRequest(handle, agnActionConnect, &user, sizeof(agnUser_t));

    return EXIT_SUCCESS;
}

int cmd_action_disconnect(agnHandle_t handle, int argc, char *argv[]) {
    agncPostActionRequest(handle, agnActionDisconnect, NULL, 0);
    return EXIT_SUCCESS;
}

int cmd_get_connect_attempt_info(agnHandle_t handle, int argc, char *argv[]) {
    agnConnectAttempt_t attempt;
    attempt.ulStructSize = sizeof(agnConnectAttempt_t);
    if (0 == agncGetConnectAttemptInfo(&attempt)) {
        replace_newlines(attempt.szStatusText);
        printf("agnConnectAttempt\tszStatusText\t%s\n", attempt.szStatusText);
        printf("agnConnectAttempt\tTimeStarted\t%lu\n", attempt.TimeStarted);
        printf("agnConnectAttempt\tTimeConnected\t%lu\n", attempt.TimeConnected);
        printf("agnConnectAttempt\tTimeCompleted\t%lu\n", attempt.TimeCompleted);
        printf("agnConnectAttempt\tVPNIPAddress\t%lu\n", attempt.VPNIPAddress);
        printf("agnConnectAttempt\tVPNServerIPAddress\t%lu\n", attempt.VPNServerIPAddress);
        printf("agnConnectAttempt\tszVPNTunnelAdapter\t%s\n", attempt.szVPNTunnelAdapter);
        printf("agnConnectAttempt\tConnectType\t%d\n", attempt.ConnectType);
        printf("agnConnectAttempt\tStatusCode\t%d\n", attempt.StatusCode);
        printf("agnConnectAttempt\tInternetIPAddress\t%lu\n", attempt.InternetIPAddress);
        printf("agnConnectAttempt\tInternetGatewayIPAddress\t%lu\n", attempt.InternetGatewayIPAddress);
        printf("agnConnectAttempt\tszInternetAdapter\t%s\n", attempt.szInternetAdapter);
        printf("agnConnectAttempt\tszInternetMACAddress\t%s\n", attempt.szInternetMACAddress);
        printf("agnConnectAttempt\tVPNCompressionActive\t%d\n", attempt.VPNCompressionActive);
        printf("agnConnectAttempt\tBytesReceivedAtStartOfConnection\t%lu\n", attempt.BytesReceivedAtStartOfConnection);
        printf("agnConnectAttempt\tBytesSentAtStartOfConnection\t%lu\n", attempt.BytesSentAtStartOfConnection);
        printf("EOF\n");
    }
    return EXIT_SUCCESS;
}

int cmd_get_state(agnHandle_t handle, int argc, char *argv[]) {
    printf("%d\nEOF\n", agncGetState());
    return EXIT_SUCCESS;
}

int cmd_get_user_info(agnHandle_t handle, int argc, char *argv[]) {
    agnUser_t user;
    user.ulStructSize = sizeof(agnUser_t);
    if (0 == agncGetUserInfo(&user)) {
        printf("agnUser\tszAccount\t%s\n", user.szAccount);
        printf("agnUser\tszNewPassword\t%s\n", user.szNewPassword);
        printf("agnUser\tszPassword\t%s\n", user.szPassword);
        printf("agnUser\tszProxyPassword\t%s\n", user.szProxyPassword);
        printf("agnUser\tszProxyServer\t%s\n", user.szProxyServer);
        printf("agnUser\tszProxyUser\t%s\n", user.szProxyUser);
        printf("agnUser\tszSMXServer\t%s\n", user.szSMXServer);
        printf("agnUser\tszUsername\t%s\n", user.szUsername);
        printf("EOF\n");
    }
    return EXIT_SUCCESS;
}
