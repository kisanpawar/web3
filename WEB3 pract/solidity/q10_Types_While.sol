// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 10 — Write a Solidity smart contract named Types that demonstrates the execution of
 * a while loop and initializes an array using the loop.
 *
 *     a. Declare a dynamic array of unsigned integers.
 *     b. Create a function that uses a while loop to insert values (e.g., 1 to 5) into the array.
 *     c. Ensure the loop runs correctly and populates the array sequentially.
 *     d. Provide another function to return the array elements.
 *     e. Use appropriate function modifiers such as public and view.
 *
 * Compile: solc --bin --abi q10_Types_While.sol
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
