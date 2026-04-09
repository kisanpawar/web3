// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 6 — Write a Solidity smart contract named Types to demonstrate the use of a while
 * loop and array initialization.
 *
 *     a. Declare a dynamic array of unsigned integers.
 *     b. Use a while loop inside a function to initialize the array with a sequence of values
 *        (e.g., 1 to 5).
 *     c. Ensure the loop correctly inserts elements into the array.
 *     d. Provide a function to return the array values.
 *     e. Use appropriate function types such as public view/pure where required.
 *
 * Compile: solc --bin --abi q06_Types_While.sol
 */

contract Types {
    uint256[] private arr;

    function fillWhile() public {
        delete arr;
        uint256 i = 1;
        while (i <= 5) {
            arr.push(i);
            unchecked {
                i++;
            }
        }
    }

    function getArray() public view returns (uint256[] memory) {
        return arr;
    }
}
