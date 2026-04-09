// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 17 — Write a Solidity smart contract named Types to demonstrate the use of the break
 * statement within a while loop.
 *
 *     a. Declare a dynamic array of unsigned integers.
 *     b. Declare an unsigned integer variable to control loop execution.
 *     c. Create a function that uses a while loop to insert values into the array.
 *     d. Use a break statement to terminate the loop when a specific condition is met (e.g., when
 *        the value reaches a limit).
 *     e. Provide a function to return the array elements.
 *
 * QUESTION 18 — Same wording as Question 17 (duplicate in practical list).
 *
 * Compile: solc --bin --abi q17_Types_Break.sol
 */

contract Types {
    uint256[] private arr;
    uint256 public limit = 3;

    function fillWithBreak() public {
        delete arr;
        uint256 i = 1;
        while (true) {
            arr.push(i);
            if (i >= limit) {
                break;
            }
            unchecked {
                i++;
            }
        }
    }

    function getArray() public view returns (uint256[] memory) {
        return arr;
    }
}
