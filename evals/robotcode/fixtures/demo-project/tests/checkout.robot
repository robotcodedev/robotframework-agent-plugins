*** Settings ***
Documentation       "Just added" suite for the analyze-before-run eval.
...                 It contains a deliberate static issue: 'Finalize Checkout'
...                 is not defined anywhere, so `robotcode analyze code` reports
...                 a KeywordNotFound without the suite ever being executed.

Resource            ../orders.resource


*** Test Cases ***
Checkout Completes
    [Tags]    checkout
    ${order}=    Submit Order    42
    Finalize Checkout    ${order}
