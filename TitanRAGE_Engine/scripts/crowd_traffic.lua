local CrowdDirector = { wanted_stars = 0, active_vehicles = 12, active_peds = 45 }

function CrowdDirector:update_city_sector(gunshots_fired, rain_intensity)
    if gunshots_fired > 0 then
        self.wanted_stars = math.min(5, self.wanted_stars + 1)
        self.active_peds = math.max(5, self.active_peds - 20)
    end
    local speed_limit = rain_intensity > 0.5 and 35.0 or 55.0
    return self.wanted_stars, speed_limit
end

local stars, limit = CrowdDirector:update_city_sector(2, 0.8)
assert(stars == 1 and limit == 35.0)
print("RAGE Crowd & Traffic AI Director Verified! Wanted Stars:", stars, "Wet Speed Limit:", limit)
