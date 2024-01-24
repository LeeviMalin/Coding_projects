#include "datastructures.hh"

#include <random>
#include <cmath>

#include <unordered_map>
#include <map>
#include <set>
#include <utility>
#include <algorithm>

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

// Returns list of all station IDs in datastructures
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
    if (stationList.count(stationid) == 1 and // check for station
        stationList.at(stationid).trainList.count(trainid) == 1 // check for trains at the station
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
        if (itr->second >= time) { // compare dep time to given time
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

    // if no same regions are found returns this
    return NO_REGION;
}

// ****************
// private functions
// ****************

// adds recursively all parent regions of a subregions to pregs container
void Datastructures::parentRegions(RegionID id)
{
    RegionID parent = regionList.at(id).parentRegion;
    pregs.push_back(id);
    if (parent != NO_REGION) {
        parentRegions(parent);
    }
    return;
}

// adds revursively subregions of a region to osubregs container
void Datastructures::subRegions(RegionID id) 
{
    for (RegionID subr : regionList.at(id).subRegions) {
        subregs.push_back(subr);
        if (regionList.at(subr).subRegions.size() != 0) {
            subRegions(subr);
        }
    }
    return;
}

