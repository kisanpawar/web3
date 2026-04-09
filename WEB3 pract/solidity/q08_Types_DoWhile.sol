// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
 * QUESTION 8 — Write a Solidity smart contract named Types to demonstrate the use of a do-while
 * loop and array initialization.
 *
 *     a. Use a do-while loop inside a function to initialize the array with a sequence of
 *        values (e.g., 1 to 5).
 *     b. Ensure that the loop executes at least once and correctly inserts elements into the array.
 *     c. Provide a function to return the array values.
 *     d. Use appropriate function types such as public view/pure where required.
 *
 * Note: Solidity has no native do-while; fillDoWhileStyle() emulates do-while semantics.
 *
 * Compile: solc --bin --abi q08_Types_DoWhile.sol
 */

contract Types {
    uint256[] private arr;

    function fillDoWhileStyle() public {
        delete arr;
        uint256 i = 1;
        bool first = true;
        while (first || i <= 5) {
            arr.push(i);
            if (i == 5) {
                break;
            }
            unchecked {
                i++;
            }
            first = false;
        }
    }

    function getArray() public view returns (uint256[] memory) {
        return arr;
    }
}
