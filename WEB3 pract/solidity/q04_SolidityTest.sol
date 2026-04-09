// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 4 — Write a Solidity smart contract named SolidityTest to demonstrate the use of
 * different arithmetic operators.
 *
 *     a. Declare two integer variables and initialize them with suitable values.
 *     b. Implement separate functions (or a single function) to perform the following
 *        arithmetic operations: Addition (+), Subtraction (-), Multiplication (x),
 *        Division (/), Modulus (%).
 *     c. Each function should return the result of the respective operation.
 *     d. Ensure appropriate use of public view/pure functions.
 *
 * Compile: solc --bin --abi q04_SolidityTest.sol
 */

contract SolidityTest {
    uint256 private x = 20;
    uint256 private y = 4;

    function add() public view returns (uint256) {
        return x + y;
    }

    function subtract() public view returns (uint256) {
        return x - y;
    }

    function multiply() public view returns (uint256) {
        return x * y;
    }

    function divide() public view returns (uint256) {
        return x / y;
    }

    function modulus() public view returns (uint256) {
        return x % y;
    }
}
