// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 20 — Write a Solidity smart contract named Test to demonstrate function calling within
 * a contract.
 *
 *     a. Define a public pure function sqrt(uint _num) that performs a mathematical operation
 *        (e.g., square of a number).
 *     b. Define another public pure function add() that:
 *     c. Return the final result obtained after the function call.
 *
 * (sqrt implements square of _num as in the practical wording; add() calls sqrt.)
 *
 * Compile: solc --bin --abi q20_Test.sol
 */

contract Test {
    function sqrt(uint256 _num) public pure returns (uint256) {
        return _num * _num;
    }

    function add() public pure returns (uint256) {
        return sqrt(7);
    }
}
