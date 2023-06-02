// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.4.22 <0.9.0;
//pragma experimental ABIEncoderV2;

/** 
 * @title SmartContract
 * @dev Control smart graden balance and regist important data
 */
contract SmartContract {

    struct MonitoringCapability {
        // data used to represent monitoring capabilities of the vehicle/cargo compartment
        string keyWord; // unique identification to monitoring capability
        int currentValue; // last value colected by the sensors about this monitoring capability
        bool exists; // verify if the monitoring capability was already added
    }

    address private owner;
    address private device;
    
    mapping(bytes32 => MonitoringCapability) private monitoringCapabilities;
    string[] private keyWords;

    mapping(address => uint256) private contributors_balance;
    // The smart contrac already matains a balance in real payment scenario
    // The next attribute was used in the test enviroment
    //uint256 gardens_balance; 

    event GardenFundsUsed(uint256 _amount, string _use, address _reciever);

    /** 
     * @dev Create a new cooler
     * @param _device Device account 
     */
    constructor(address _device ) {
        owner = msg.sender;
        device = _device;
        //gardens_balance = 0;
    }



    modifier onlyOwner {
        require(msg.sender == owner, "You are not the owner.");
        _;
    }

    /** 
     * @dev Provides cooler owner
     * @return owner_
     */
    function getOwner() public view
            returns (address owner_)
    {
        return owner;
    }

    /** 
     * @dev Contributor deposit credits
     */
    function depositCredits() payable public
    {
        //contributors_balance[msg.sender] += _amount;
        //gardens_balance += _amount;
        
        // This function is used in a testnet with zero balance accounts.
        // In a real scenario correct way is to add funs via msg.value
        contributors_balance[msg.sender] += msg.value;

    }

    /** 
     * @dev Contributor get food from garden
     * @param _amount Amount of credits used
     */
    function useCredits(uint256 _amount) public
    {
        require(balanceOf(msg.sender) >= _amount, "Insufficient credits.");
        contributors_balance[msg.sender] -= _amount;
    }

    /** 
     * @dev Provides contributor balance
     * @param _contributor_account Account address of a contributor
     * @return balance_ Current balance of the contributor 
     */
    function balanceOf(address _contributor_account) public view
            returns (uint256 balance_)
    {
        return contributors_balance[_contributor_account];
    }

    /** 
     * @dev Provides garden's balance 
     * @return balance_
     */
    function getBalance() public view
            returns (uint256 balance_)
    {
        return address(this).balance;
    }

    /** 
     * @dev Caretaker get funds from garden's balance
     * @param _amount Amount of funds used
     * @param _use Short description of the use of funds
     * @param _reciever Adress of account to receive funds
     */
    function useGardenFunds(uint256 _amount, string memory _use, address payable _reciever) public onlyOwner
    {
        //require(gardens_balance >= _amount);
        require(address(this).balance >= _amount);
        //gardens_balance -= _amount;

        // Here the funds would be tranfered.
        _reciever.transfer(_amount);

        // A voting system could be applied here, allowing all active contributors decide if the use is really necessary.

        emit GardenFundsUsed(_amount, _use, _reciever);
    }

    /** 
     * @dev Add a new monitoring capability 
     * @param _keyWord keyword of a monitoring capability
     */
    function addMonitoringCapability(string memory _keyWord) public onlyOwner
    {
        keyWords.push(_keyWord);
        monitoringCapabilities[keccak256(abi.encodePacked(_keyWord))] = (MonitoringCapability({
            keyWord: _keyWord,
            currentValue: 0,
            exists: true
        }));
    }

    /** 
     * @dev Provides monitoring capabilities visibility 
     * @return monitoringCapabilities_ comma-separated string with all available monitoring capabilities
     */
    function getMonitoringCapabilities() public view
            returns (string memory)
    {
        if(keyWords.length > 0) {
            string memory keyWords_ = keyWords[0];
            
            for (uint i = 1; i < keyWords.length; i++) {
                keyWords_ = string(abi.encodePacked(keyWords_, ", ", keyWords[i]));
            }
            return (keyWords_);
        
        } else {
            return "No monitoring capabilities registered yet.";
        }
    }

    /** 
     * @dev Update the value of a monitoring capability
     * @param _keyWord keyword of a monitoring capability
     * @param _value current value for a monitoring capability
     */
    function setMonitoringValue(string memory _keyWord, int _value) public
    {
        require(msg.sender == device);
        bytes32 key = keccak256(abi.encodePacked(_keyWord));
        if(monitoringCapabilities[key].exists){
            monitoringCapabilities[key].currentValue = _value;
        }
    }

    /** 
     * @dev Provides monitoring capability value visibility 
     * @param _keyWord keyword of a monitoring capability
     * @return monitoringCapabilityValue_ uint of the monitoring capability current value
     */
    function getMonitoringValue(string memory _keyWord) public view
            returns (int)
    {
        bytes32 key = keccak256(abi.encodePacked(_keyWord));
        if(monitoringCapabilities[key].exists)
            return monitoringCapabilities[key].currentValue;
        else
            return 0;
    }

}