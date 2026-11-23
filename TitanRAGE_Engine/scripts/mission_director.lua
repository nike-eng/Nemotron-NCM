-- Define the states of the wanted level escalation and NPC squad flanking state machine
local WANTED_LEVEL_STATES = {
    LOW = "LOW",
    MEDIUM = "MEDIUM",
    HIGH = "HIGH"
}

local FLANKING_STATES = {
    NOT_FLANKING = "NOT_FLANKING",
    FLANK_LEFT = "FLANK_LEFT",
    FLANK_RIGHT = "FLANK_RIGHT"
}

-- Initialize variables
local currentWantedLevel = WANTED_LEVEL_STATES.LOW
local currentFlankingState = FLANKING_STATES.NOT_FLANKING

-- Function to update the wanted level
function updateWantedLevel(newLevel)
    assert(WANTED_LEVEL_STATES[newLevel], "Invalid wanted level")
    currentWantedLevel = newLevel
end

-- Function to update the flanking state
function updateFlankingState(newState)
    assert(FLANKING_STATES[newState], "Invalid flanking state")
    currentFlankingState = newState
end

-- Function to handle the state transitions based on the wanted level
function handleStateTransitions()
    if currentWantedLevel == WANTED_LEVEL_STATES.LOW then
        updateFlankingState(FLANKING_STATES.NOT_FLANKING)
    elseif currentWantedLevel == WANTED_LEVEL_STATES.MEDIUM then
        updateFlankingState(math.random(2) == 1 and FLANK_LEFT or FLANK_RIGHT)
    elseif currentWantedLevel == WANTED_LEVEL_STATES.HIGH then
        updateFlankingState(math.random(3) == 1 and FLANK_LEFT or math.random(3) == 2 and FLANK_RIGHT or FLANK_LEFT)
    end
end

-- Self-test function to verify the correctness of the state machine
function selfTest()
    -- Test initial state
    assert(currentWantedLevel == WANTED_LEVEL_STATES.LOW, "Initial wanted level should be LOW")
    assert(currentFlankingState == FLANKING_STATES.NOT_FLANKING, "Initial flanking state should be NOT_FLANKING")

    -- Test state transition from LOW to MEDIUM
    updateWantedLevel(WANTED_LEVEL_STATES.MEDIUM)
    assert(currentWantedLevel == WANTED_LEVEL_STATES.MEDIUM, "Wanted level should be MEDIUM after transition")
    assert(currentFlankingState ~= FLANKING_STATES.NOT_FLANKING, "Flanking state should not be NOT_FLANKING after transition")

    -- Test state transition from MEDIUM to HIGH
    updateWantedLevel(WANTED_LEVEL_STATES.HIGH)
    assert(currentWantedLevel == WANTED_LEVEL_STATES.HIGH, "Wanted level should be HIGH after transition")
    assert(currentFlankingState ~= FLANKING_STATES.NOT_FLANKING, "Flanking state should not be NOT_FLANKING after transition")

    -- Test state transition from HIGH back to MEDIUM
    updateWantedLevel(WANTED_LEVEL_STATES.MEDIUM)
    assert(currentWantedLevel == WANTED_LEVEL_STATES.MEDIUM, "Wanted level should be MEDIUM after transition")
    assert(currentFlankingState ~= FLANKING_STATES.NOT_FLANKING, "Flanking state should not be NOT_FLANKING after transition")

    -- Test state transition from MEDIUM back to LOW
    updateWantedLevel(WANTED_LEVEL_STATES.LOW)
    assert(currentWantedLevel == WANTED_LEVEL_STATES.LOW, "Wanted level should be LOW after transition")
    assert(currentFlankingState == FLANKING_STATES.NOT_FLANKING, "Flanking state should be NOT_FLANKING after transition")

    print("All self-tests passed!")
end

-- Run the self-test
selfTest()

-- Example usage of the state machine
updateWantedLevel(WANTED_LEVEL_STATES.MEDIUM)
handleStateTransitions()
print("Current Flanking State:", currentFlankingState)

updateWantedLevel(WANTED_LEVEL_STATES.HIGH)
handleStateTransitions()
print("Current Flanking State:", currentFlankingState)


This Lua script defines a simple state machine for managing the escalation of a wanted level and the flanking behavior of an NPC squad. The `updateWantedLevel` and `updateFl