*** Settings ***
Documentation       Order suite for the demo fixture — these all pass.

Resource            ../orders.resource


*** Test Cases ***
Shipped Order Has Status Shipped
    [Tags]    smoke    orders
    Order Status Should Be    42    shipped

Pending Order Has Status Pending
    [Tags]    orders
    Order Status Should Be    7    pending

Submit Order Returns The Record
    [Tags]    orders
    ${order}=    Submit Order    42
    Should Be Equal    ${order}[item]    widget
