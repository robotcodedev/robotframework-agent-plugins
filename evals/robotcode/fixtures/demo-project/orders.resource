*** Settings ***
Documentation       Reusable keywords for the demo fixture, backed by OrderLibrary.

Library             OrderLibrary


*** Keywords ***
Login With Credentials
    [Documentation]    Attempt a login and return the backend response dict.
    [Arguments]    ${username}    ${password}
    ${response}=    Get Login Response    ${username}    ${password}
    RETURN    ${response}

Submit Order
    [Documentation]    Look up an order by id and return its record.
    ...    Raises if the order does not exist.
    [Arguments]    ${order_id}
    ${order}=    Get Order    ${order_id}
    RETURN    ${order}

Order Status Should Be
    [Documentation]    Assert the stored status of an order.
    [Arguments]    ${order_id}    ${expected}
    ${status}=    Get Order Status    ${order_id}
    Should Be Equal    ${status}    ${expected}
