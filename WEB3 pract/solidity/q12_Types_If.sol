// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 12 — Write a Solidity smart contract named Types to demonstrate the use of an if
 * statement. The contract should perform the following tasks:
 *
 *     a. Declare an unsigned integer state variable.
 *     b. Create a function that assigns a value to the variable.
 *     c. Use an if statement to check a condition (e.g., whether the value is greater than a
 *        specific number).
 *     d. Based on the condition, return an appropriate result (e.g., "Greater" or "Smaller").
 *
 * Compile: solc --bin --abi q12_Types_If.sol
 */

contract Types {
    uint256 public value;

    function setAndCompare(uint256 v) public returns (string memory) {
        value = v;
        if (value > 10) {
            return "Greater";
        }
        return "Smaller";
    }
}
