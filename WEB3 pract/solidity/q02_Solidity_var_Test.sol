// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 2 — Write a Solidity smart contract named Solidity_var_Test that performs the following:
 *
 *     a. Declare two local variables inside a function.
 *     b. Initialize these variables with suitable integer values.
 *     c. Create a function that calculates and returns the sum of the two local variables.
 *     d. Ensure the function is declared as a public view/pure function.
 *
 * Compile: solc --bin --abi q02_Solidity_var_Test.sol
 */

contract Solidity_var_Test {
    function sumLocals() public pure returns (uint256) {
        uint256 a = 10;
        uint256 b = 20;
        return a + b;
    }
}
