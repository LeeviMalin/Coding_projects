#include "datastructures.hh"

#include <random>
#include <cmath>

#include <unordered_map>
#include <map>
#include <set>
#include <utility>
#include <algorithm>
#include <queue>

std::minstd_rand rand_engine; // Reasonably quick pseudo-random generator

template <typename Type>
Type random_in_range(Type start, Type end)
{
    auto range = end-start;
    ++range;

    auto num = std::uniform_int_distribution<unsigned long int>(0, range-1)(rand_engine);

    return static_cast<Type>(start+num);
}

Datastructures::Datastructures()
{    
}

Datastructures::~Datastructures()
{   
}

unsigned int Datastructures::station_count()
{
    return stationList.size();
}

void Datastructures::clear_all()
{
    stationList.clear();
    regionList.clear();
    distanceFirst.clear();
    nameFirst.clear();
}

std::vector<StationID> Datastructures::all_stations()
{
    std::vector<StationID> IDs;
    if (stationList.empty()) {
        return IDs;
    } else {
        for (auto itr = stationList.begin() ; itr != stationList.end() ; itr++)  {
            IDs.push_back(itr->first);
        }
    }
    return IDs;
}

bool Datastructures::add_station(StationID id, const Name& name, Coord xy)
{
    if (stationList.count(id) == 1) {
        return false;
    } else {
    stationList[id].name = name;
    stationList[id].coordinates = xy;
    distanceFirst[xy] = id;
    nameFirst[name] = id;
    return true;
    }
}

Name Datastructures::get_station_name(StationID id)
{
    if (stationList.count(id) == 0) {
        return NO_NAME;
    } else {
        return stationList.at(id).name;
    }
}

Coord Datastructures::get_station_coordinates(StationID id)
{
    if (stationList.count(id) == 0) {
       return NO_COORD;
    } else {
        return stationList.at(id).coordinates;
    }
}

std::vector<StationID> Datastructures::stations_alphabetically()
{
    std::vector<StationID> orderedID;
    for (const auto& member : nameFirst) {
        orderedID.push_back(member.second);
    }
    return orderedID;
}

std::vector<StationID> Datastructures::stations_distance_increasing()
{    
    std::vector<StationID> orderedID;
    for (auto itr = distanceFirst.begin() ; itr != distanceFirst.end() ; itr++) {
        orderedID.push_back(itr->second);
    }
    return orderedID;
}

StationID Datastructures::find_station_with_coord(Coord xy)
{            
    if (distanceFirst.count(xy) == 0) {
        return NO_STATION;
    }
    return distanceFirst.at(xy);
}

bool Datastructures::change_station_coord(StationID id, Coord newcoord)
{
    if (stationList.count(id) == 0) {
        return false;
    } else {

    distanceFirst.erase(stationList.at(id).coordinates);
    stationList.at(id).coordinates = newcoord;
    distanceFirst[newcoord] = id;
    return true;
    }
}

// *************************
// Commands for trains
// *************************

bool Datastructures::add_departure(StationID stationid, TrainID trainid, Time time)
{
    if (stationList.count(stationid) == 1 and // Station already exists
        stationList.at(stationid).trainList.count(trainid) == 0 // Train does not exist
            ) {
        stationList[stationid].trainList[trainid] = time;
        return true;
    }
    return false;
}

bool Datastructures::remove_departure(StationID stationid, TrainID trainid, Time /*time*/)
{
    if (stationList.count(stationid) == 1 and
        stationList.at(stationid).trainList.count(trainid) == 1 
        ) {
        stationList.at(stationid).trainList.erase(trainid);
        return true;
    }
    return false;
}

// Returns list of departues at given station after given time
std::vector<std::pair<Time, TrainID>> Datastructures::station_departures_after(StationID stationid, Time time)
{
    std::vector<std::pair<Time,TrainID>> depList;

    // checks for station and train existance 
    if (stationList.count(stationid) == 0) {
        std::pair<Time,TrainID> info (NO_TIME,NO_TRAIN);
        depList.push_back(info);
        return depList;
    } else if (stationList.at(stationid).trainList.size() == 0) {
        return depList;
    } else {
    // Loop goes through all trains at the station
    for (auto itr = stationList.at(stationid).trainList.begin() ; itr != stationList.at(stationid).trainList.end() ; itr++) {
        if (itr->second >= time) {// compare dep time to given time
            std::pair<Time,TrainID> info (itr->second,itr->first);
            depList.push_back(info);
        }
    }
    std::sort(depList.begin(),depList.end());
    return depList;
    }
}

// ******************************
// Commands for regions
// ******************************

bool Datastructures::add_region(RegionID id, const Name& name, std::vector<Coord> coords)
{
    if (regionList.count(id) == 1) {
        return false;
    } else {
        regionList[id].name = name;
        regionList[id].area = coords;
    }
    return true;
}

std::vector<RegionID> Datastructures::all_regions()
{
    std::vector<RegionID> list;
    for (auto itr = regionList.begin() ; itr != regionList.end() ; itr++) {
        list.push_back(itr->first);
    }
    return list;
}

Name Datastructures::get_region_name(RegionID id)
{
    if (regionList.count(id) == 0) {
        return NO_NAME;
    }
    return regionList.at(id).name;
}

std::vector<Coord> Datastructures::get_region_coords(RegionID id)
{
    if (regionList.count(id) == 0) {
        std::vector<Coord> v {NO_COORD};
        return v;
    }
    return regionList.at(id).area;
}

bool Datastructures::add_subregion_to_region(RegionID id, RegionID parentid)
{
    if (regionList.count(id) == 0) {
        return false;
    }
    if (regionList.at(id).parentRegion != NO_REGION) {
        return false;
    }
    regionList.at(id).parentRegion = parentid;
    regionList.at(parentid).subRegions.push_back(id);
    return true;
}

bool Datastructures::add_station_to_region(StationID id, RegionID parentid)
{
    if (stationList.count(id) == 0 or regionList.count(parentid) == 0) {
        return false;
    }
    stationList.at(id).parentRegion = parentid;
    regionList.at(parentid).stations.push_back(id);
    return true;
}

// Returns vector of regions a station is assinged to
// Returns vector with NO_REGION if no regions are found
std::vector<RegionID> Datastructures::station_in_regions(StationID id)
{
    std::vector<RegionID> errorvec;
    pregs.clear();
    if (stationList.count(id) == 0) {
        errorvec.push_back(NO_REGION);
        return errorvec;
    } else if (stationList.at(id).parentRegion == NO_REGION) {
        return errorvec;
    }

    RegionID stationsRegion = stationList.at(id).parentRegion;

    parentRegions(stationsRegion);
    return pregs;
}

// *********************
// Extra commands
// *********************

std::vector<RegionID> Datastructures::all_subregions_of_region(RegionID id)
{
    subregs.clear();
    if (regionList.count(id) == 0) {
        subregs.push_back(NO_REGION);
        return subregs;
    }
    subregs.clear();
    if (regionList.at(id).subRegions.size() == 0) {
        return subregs;
    }
    subRegions(id);
    return subregs;
}

std::vector<StationID> Datastructures::stations_closest_to(Coord xy)
{
     // This algorithm never worked :(
    throw NotImplemented("stations_closest_to()");

    std::vector<StationID> orderedIDs;
    std::map<Distance,StationID> closest;
    if (distanceFirst.count(xy) == 0) {
        return orderedIDs;
    }
    auto itr = distanceFirst.find(xy);

    auto itrf = itr;
    // Loop calculates three next stations according to total distance
    // from sorted stations distance coords 
    for (int i = 0; i < 3 ; i++) {
        Distance dis = (pow(xy.x - itrf->first.x,2) + pow(xy.y - itrf->first.y,2));
        closest[dis] = itrf->second;
        itrf++;
    }
    for (int i = 0; i < 3 ; i++) {
        Distance dis = (pow(xy.x - itr->first.x,2) + pow(xy.y - itr->first.y,2));
        closest[dis] = itr->second;
        itr--;
    }
    for (auto member : closest) {
            orderedIDs.push_back(member.second);
    }
    return orderedIDs;
}

bool Datastructures::remove_station(StationID id)
{
    if (stationList.count(id) == 0) {
        return false;
    }
    //removes from distance container
    for (auto member : distanceFirst) {
        if (member.second == id) {
            distanceFirst.erase(member.first);
            break;
        }
    }
    //removes from name container
    for (auto member : nameFirst) {
        if (member.second == id) {
            nameFirst.erase(member.first);
            break;
        }
    }
    //removes from regionList container
    for (auto member : regionList) {
        auto itr = std::find(member.second.stations.begin(),member.second.stations.end(),id);
        if (itr != member.second.stations.end()) {
            member.second.stations.erase(itr);
        }
    }

    stationList.erase(id);
    return true;
}

// finds common parent of two regions
RegionID Datastructures::common_parent_of_regions(RegionID id1, RegionID id2)
{
    if (regionList.count(id1) == 0 or regionList.count(id2) == 0) {
        return NO_REGION;
    }
    parentRegions(id1);
    std::vector<RegionID> parents1 = pregs;
    pregs.clear();
    parentRegions(id2);
    std::vector<RegionID> parents2 = pregs;
    pregs.clear();

    // loops all parents and finds the same ones 
    for (auto member1 : parents1) {
        for (auto member2 : parents2) {
            if (member1 == member2) {
                return member1;
            }
        }
    }
    return NO_REGION;
}

// ******************
// PRG2 commands
// ******************

bool Datastructures::add_train(TrainID trainid, std::vector<std::pair<StationID, Time> > stationtimes)
{
    if (trainList.count(trainid) == 1) {
        return false;
    }
    auto it = stationtimes.begin();
    while (it != stationtimes.end() - 1) {
        if (stationList.count(it->first) == 0) {
            return false;
        }

        auto previousStation = it;
        it++;

        trainList[trainid].stations = stationtimes;

        //Distance between the sations
        int t1 = pow(stationList.at(it->first).coordinates.x-stationList.at(previousStation->first).coordinates.x,2);
        int t2 = pow(stationList.at(it->first).coordinates.y-stationList.at(previousStation->first).coordinates.y,2);
        Distance dis = sqrt(t1 + t2);
        // Add neighbours to stations
        stationList.at(previousStation->first).neighbours[it->first] = dis;
    }
    return true;
}

// Finds staions adjacent to given station and returns them in vector
std::vector<StationID> Datastructures::next_stations_from(StationID id)
{
    std::vector<StationID> resultvec;
    if (stationList.count(id) == 0) {
        resultvec.push_back(NO_STATION);
        return resultvec;
    }

    for (auto member : stationList.at(id).neighbours) {
        resultvec.push_back(member.first);
    }
    return resultvec;
}

std::vector<StationID> Datastructures::train_stations_from(StationID stationid, TrainID trainid)
{    
    std::vector<StationID> resultvec;
    std::vector<std::pair<StationID, Time>>::iterator fiter;
    //Check for exeptions
    if (stationList.count(stationid) == 0 or trainList.count(trainid) == 0) {
        resultvec.push_back(NO_STATION);
        return resultvec;
    }
    for (auto& mem : stationList.at(stationid).trainList) {
        if (mem.first == trainid) {
            break;
        }
        resultvec.push_back(NO_STATION);
        return resultvec;
    }

    // Find itr from trains station container from which
    // we find the stations
    for (auto it = trainList.at(trainid).stations.begin() ; it != trainList.at(trainid).stations.end() ; it++) {
        if (it->first == trainList.at(trainid).stations.back().first) {
            resultvec.push_back(NO_STATION);
            return resultvec;
        }
        if (it->first == stationid) {
            fiter = it;
            fiter ++;
            while (fiter != trainList.at(trainid).stations.end()) {
                resultvec.push_back(fiter->first);
                fiter++;
            }
            return resultvec;
        }
    }
    // if no stations are found returns no station
    resultvec.push_back(NO_STATION);
    return resultvec;
}

void Datastructures::clear_trains()
{
    for (auto& member : stationList) {
        member.second.trainList.clear();
        member.second.neighbours.clear();
    }
    trainList.clear();
}

// finds some route between two stations
std::vector<std::pair<StationID, Distance>> Datastructures::route_any(StationID fromid, StationID toid)
{
    for (auto& mem : stationList) {
        std::pair<StationID,Distance> def = {NO_STATION,NO_DISTANCE};
        mem.second.from = def;
    }
    route.clear();
    setWhite();
    std::queue<std::pair<StationID,Time>> Q;
    std::vector<std::pair<StationID,Distance>> resultvec;

    if (stationList.count(fromid) == 0 or stationList.count(toid) == 0) {
        resultvec.push_back({NO_STATION,NO_DISTANCE});
        return resultvec;
    }

    stationList.at(fromid).colour = 1;
    Q.push({fromid,0});
    while (!Q.empty()) {
        std::pair<StationID,Distance> u = Q.front();
        Q.pop();
        for (auto v : stationList.at(u.first).neighbours) {
            if (stationList.at(v.first).colour == 2) {
                stationList.at(v.first).colour = 1;
                v.second = v.second + u.second;
                stationList.at(v.first).from = u;
                Q.push(v);
            }
            // Do this when id is found
            if (v.first == toid) {
                //trackRoute(v,0);
                trackRoute(v);
                std::reverse(route.begin(),route.end());
                std::pair<StationID,Distance> pari;
                return route;
            }
        }
        stationList.at(u.first).colour = 0;
    }
    return resultvec;
}

// ***************
// Extra functions
// ***************

std::vector<std::pair<StationID, Distance>> Datastructures::route_least_stations(StationID fromid, StationID toid)
{
    for (auto& mem : stationList) {
        std::pair<StationID,Distance> def = {NO_STATION,NO_DISTANCE};
        mem.second.from = def;
    }
    route.clear();
    setWhite();
    std::queue<std::pair<StationID,Time>> Q;
    std::vector<std::pair<StationID,Distance>> resultvec;

    if (stationList.count(fromid) == 0 or stationList.count(toid) == 0) {
        resultvec.push_back({NO_STATION,NO_DISTANCE});
        return resultvec;
    }


    stationList.at(fromid).colour = 1;
    Q.push({fromid,0});
    while (!Q.empty()) {
        std::pair<StationID,Distance> u = Q.front();
        Q.pop();
        for (auto v : stationList.at(u.first).neighbours) {
            if (stationList.at(v.first).colour == 2) {
                stationList.at(v.first).colour = 1;
                v.second = v.second + u.second;
                stationList.at(v.first).from = u;
                Q.push(v);
            }
            if (v.first == toid) {
                trackRoute(v);
                std::reverse(route.begin(),route.end());
                std::pair<StationID,Distance> pari;
                return route;
            }
        }
        stationList.at(u.first).colour = 0;
    }
    return resultvec;
}

std::vector<StationID> Datastructures::route_with_cycle(StationID /*fromid*/)
{
    throw NotImplemented("route_witch_cycle");
    /*
     * Broken depth first algorithm
    std::stack<std::pair<StationID,Time>> S;
    std::vector<std::pair<StationID,Distance>> resultvec;

    if (stationList.count(fromid) == 0 or stationList.count(toid) == 0) {
        resultvec.push_back({NO_STATION,NO_DISTANCE});
        return resultvec;
    }
    setWhite();

    S.push({fromid,0});

    while (!S.empty()) {
        std::pair<StationID,Distance> newmem = S.top();
        S.pop();
        if (stationList.at(newmem.first).colour == 2) {
            stationList.at(newmem.first).colour = 1;
            S.push(newmem);
            for (auto member : stationList.at(newmem.first).neighbours) {
                if (stationList.at(member.first).colour == 2) {
                    Distance currentDist = S.top().second + member.second;
                    S.push({member.first,currentDist});
                } else if (stationList.at(member.first).colour == 1) {
                    return resultvec;
                }
                if (member.first == toid) {
                    for (unsigned int n = 0 ; n <= S.size() ; n++) {
                        resultvec.push_back(S.top());
                        S.pop();
                    }
                    reverse(resultvec.begin(),resultvec.end());
                    return resultvec;
                }
            }
        } else {
            stationList.at(newmem.first).colour = 0;
        }
    }

    return resultvec;
    */
    
}

std::vector<std::pair<StationID, Distance>> Datastructures::route_shortest_distance(StationID /*fromid*/, StationID /*toid*/)
{
    // Replace the line below with your implementation
    // Also uncomment parameters ( /* param */ -> param )
    throw NotImplemented("route_shortest_distance()");
}

std::vector<std::pair<StationID, Time>> Datastructures::route_earliest_arrival(StationID /*fromid*/, StationID /*toid*/, Time /*starttime*/)
{
    // Replace the line below with your implementation
    // Also uncomment parameters ( /* param */ -> param )
    throw NotImplemented("route_earliest_arrival()");
}

// ****************
// Private functions
// ****************

void Datastructures::parentRegions(RegionID id)
{
    RegionID parent = regionList.at(id).parentRegion;
    pregs.push_back(id);
    if (parent != NO_REGION) {
        parentRegions(parent);
    }
    return;
}

void Datastructures::subRegions(RegionID id) {

    for (RegionID subr : regionList.at(id).subRegions) {
        subregs.push_back(subr);
        if (regionList.at(subr).subRegions.size() != 0) {
            subRegions(subr);
        }
    }
    return;
}

void Datastructures::trackRoute(std::pair<StationID, Distance> current)
{
    std::pair<StationID,Distance> endpair = {NO_STATION,NO_DISTANCE};
    if (current == endpair) {
        return;
    }
    route.push_back(current);
    trackRoute(stationList.at(current.first).from);
}

void Datastructures::setWhite()
{
    for (auto& member : stationList) {
        member.second.colour = 2;
    }
}



