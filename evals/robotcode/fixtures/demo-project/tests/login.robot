*** Settings ***
Documentation       Login suite for the demo fixture.
...                 'Login Works' fails by default (wrong password), so the debugger
...                 and results evals have a real failure — and a ${response} dict — to
...                 inspect. The test setup's baseline run overrides ${PASSWORD} to get
...                 a passing run to diff the failing one against.

Resource            ../orders.resource


*** Variables ***
${USERNAME}         alice
# Wrong by default → 'Login Works' fails. setup.sh's baseline run overrides this
# with -v PASSWORD:'correct horse' to produce a passing baseline.
${PASSWORD}         wrong-password


*** Test Cases ***
Login Works
    [Documentation]    Logs in and expects success. Fails by default because
    ...    ${PASSWORD} is wrong, so the backend returns status=error.
    [Tags]    smoke    login
    ${response}=    Login With Credentials    ${USERNAME}    ${PASSWORD}
    Log    Got login response: ${response}
    Should Be Equal    ${response}[status]    ok
    ...    msg=Login should have succeeded but the backend rejected the credentials

Login Rejects Empty Password
    [Tags]    login
    ${response}=    Login With Credentials    ${USERNAME}    ${EMPTY}
    Should Be Equal    ${response}[status]    error
