// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 14 — Write a Solidity smart contract named Types to demonstrate the use of an if-else
 * statement.
 *
 *     a. Declare a state variable (e.g., an unsigned integer).
 *     b. Create a function to assign a value to the state variable.
 *     c. Use an if-else statement to check a condition (e.g., whether the value is greater than a
 *        given number).
 *     d. Return different outputs based on the condition (e.g., "Greater" or "Not Greater").
 *
 * Compile: solc --bin --abi q14_Types_IfElse.sol
 */

contract Types {
    uint256 public value;

    function setAndBranch(uint256 v) public returns (string memory) {
        value = v;
        if (value > 10) {
            return "Greater";
        } else {
            return "Not Greater";
        }
    }
}
