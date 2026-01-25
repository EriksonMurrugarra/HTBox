import '../../../style/devicelist.css';
import { BaseDeviceTracker } from '../../client/BaseDeviceTracker';
import { SERVER_PORT } from '../../../common/Constants';
import { ACTION } from '../../../common/Action';
import GoogDeviceDescriptor from '../../../types/GoogDeviceDescriptor';
import { ControlCenterCommand } from '../../../common/ControlCenterCommand';
import { StreamClientScrcpy } from './StreamClientScrcpy';
import SvgImage from '../../ui/SvgImage';
import Util from '../../Util';
import { Attribute } from '../../Attribute';
import { DeviceState } from '../../../common/DeviceState';
import { Message } from '../../../types/Message';
import { ParamsDeviceTracker } from '../../../types/ParamsDeviceTracker';
import { HostItem } from '../../../types/Configuration';
import { ChannelCode } from '../../../common/ChannelCode';
import { Tool } from '../../client/Tool';

type Field = keyof GoogDeviceDescriptor | ((descriptor: GoogDeviceDescriptor) => string);
type DescriptionColumn = { title: string; field: Field };

const DESC_COLUMNS: DescriptionColumn[] = [
    {
        title: 'Net Interface',
        field: 'interfaces',
    },
    {
        title: 'Server PID',
        field: 'pid',
    },
];

export class DeviceTracker extends BaseDeviceTracker<GoogDeviceDescriptor, never> {
    public static readonly ACTION = ACTION.GOOG_DEVICE_LIST;
    public static readonly CREATE_DIRECT_LINKS = true;
    private static instancesByUrl: Map<string, DeviceTracker> = new Map();
    protected static tools: Set<Tool> = new Set();
    protected tableId = 'goog_device_list';

    public static start(hostItem: HostItem): DeviceTracker {
        const url = this.buildUrlForTracker(hostItem).toString();
        let instance = this.instancesByUrl.get(url);
        if (!instance) {
            instance = new DeviceTracker(hostItem, url);
        }
        return instance;
    }

    public static getInstance(hostItem: HostItem): DeviceTracker {
        return this.start(hostItem);
    }

    protected constructor(params: HostItem, directUrl: string) {
        super({ ...params, action: DeviceTracker.ACTION }, directUrl);
        DeviceTracker.instancesByUrl.set(directUrl, this);
        this.buildDeviceTable();
        this.openNewConnection();
    }

    protected onSocketOpen(): void {
        // nothing here;
    }

    protected setIdAndHostName(id: string, hostName: string): void {
        super.setIdAndHostName(id, hostName);
        for (const value of DeviceTracker.instancesByUrl.values()) {
            if (value.id === id && value !== this) {
                console.warn(
                    `Tracker with url: "${this.url}" has the same id(${this.id}) as tracker with url "${value.url}"`,
                );
                console.warn(`This tracker will shut down`);
                this.destroy();
            }
        }
    }

    onInterfaceSelected = (event: Event): void => {
        const selectElement = event.currentTarget as HTMLSelectElement;
        const option = selectElement.selectedOptions[0];
        const url = decodeURI(option.getAttribute(Attribute.URL) || '');
        const name = option.getAttribute(Attribute.NAME) || '';
        const fullName = decodeURIComponent(selectElement.getAttribute(Attribute.FULL_NAME) || '');
        const udid = selectElement.getAttribute(Attribute.UDID) || '';
        this.updateLink({ url, name, fullName, udid, store: true });
        // Update iframes when interface changes
        this.buildDeviceIframes();
    };

    private updateLink(params: { url: string; name: string; fullName: string; udid: string; store: boolean }): void {
        const { url, name, fullName, udid, store } = params;
        const playerTds = document.getElementsByName(
            encodeURIComponent(`${DeviceTracker.AttributePrefixPlayerFor}${fullName}`),
        );
        if (typeof udid !== 'string') {
            return;
        }
        if (store) {
            const localStorageKey = DeviceTracker.getLocalStorageKey(fullName || '');
            if (localStorage && name) {
                localStorage.setItem(localStorageKey, name);
            }
        }
        const action = ACTION.STREAM_SCRCPY;
        playerTds.forEach((item) => {
            item.innerHTML = '';
            const playerFullName = item.getAttribute(DeviceTracker.AttributePlayerFullName);
            const playerCodeName = item.getAttribute(DeviceTracker.AttributePlayerCodeName);
            if (!playerFullName || !playerCodeName) {
                return;
            }
            const link = DeviceTracker.buildLink(
                {
                    action,
                    udid,
                    player: decodeURIComponent(playerCodeName),
                    ws: url,
                },
                decodeURIComponent(playerFullName),
                this.params,
            );
            item.appendChild(link);
        });
    }

    onActionButtonClick = (event: MouseEvent): void => {
        const button = event.currentTarget as HTMLButtonElement;
        const udid = button.getAttribute(Attribute.UDID);
        const pidString = button.getAttribute(Attribute.PID) || '';
        const command = button.getAttribute(Attribute.COMMAND) as string;
        const pid = parseInt(pidString, 10);
        const data: Message = {
            id: this.getNextId(),
            type: command,
            data: {
                udid: typeof udid === 'string' ? udid : undefined,
                pid: isNaN(pid) ? undefined : pid,
            },
        };

        if (this.ws && this.ws.readyState === this.ws.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    };

    private static getLocalStorageKey(udid: string): string {
        return `device_list::${udid}::interface`;
    }

    protected static createUrl(params: ParamsDeviceTracker, udid = ''): URL {
        const secure = !!params.secure;
        const hostname = params.hostname || location.hostname;
        const port = typeof params.port === 'number' ? params.port : secure ? 443 : 80;
        const pathname = params.pathname || location.pathname;
        const urlObject = this.buildUrl({ ...params, secure, hostname, port, pathname });
        if (udid) {
            urlObject.searchParams.set('action', ACTION.PROXY_ADB);
            urlObject.searchParams.set('remote', `tcp:${SERVER_PORT.toString(10)}`);
            urlObject.searchParams.set('udid', udid);
        }
        return urlObject;
    }

    protected static createInterfaceOption(name: string, url: string): HTMLOptionElement {
        const optionElement = document.createElement('option');
        optionElement.setAttribute(Attribute.URL, url);
        optionElement.setAttribute(Attribute.NAME, name);
        optionElement.innerText = `proxy over adb`;
        return optionElement;
    }

    private static titleToClassName(title: string): string {
        return title.toLowerCase().replace(/\s/g, '_');
    }

    protected buildDeviceTable(): void {
        super.buildDeviceTable();
        // Build iframes for active devices after building the table
        this.buildDeviceIframes();
    }

    protected buildDeviceRow(tbody: Element, device: GoogDeviceDescriptor): void {
        let selectedInterfaceUrl = '';
        let selectedInterfaceName = '';
        const blockClass = 'desc-block';
        const fullName = `${this.id}_${Util.escapeUdid(device.udid)}`;
        const isActive = device.state === DeviceState.DEVICE;
        let hasPid = false;
        const servicesId = `device_services_${fullName}`;
        const collapseButtonId = `collapse_${fullName}`;
        
        // Create collapse button
        const collapseButton = document.createElement('button');
        collapseButton.id = collapseButtonId;
        collapseButton.className = 'device-collapse-button';
        collapseButton.innerHTML = '▶';
        collapseButton.setAttribute('aria-label', 'Toggle device details');
        
        // Create header left section
        const headerLeft = document.createElement('div');
        headerLeft.className = 'device-header-left';
        headerLeft.appendChild(collapseButton);
        
        const deviceName = document.createElement('div');
        deviceName.className = 'device-name';
        deviceName.textContent = `${device['ro.product.manufacturer']} ${device['ro.product.model']}`;
        headerLeft.appendChild(deviceName);
        
        // Create header right section
        const headerRight = document.createElement('div');
        headerRight.className = 'device-header-right';
        
        const deviceState = document.createElement('div');
        deviceState.className = 'device-state';
        deviceState.title = `State: ${device.state}`;
        headerRight.appendChild(deviceState);
        
        // Create header
        const header = document.createElement('div');
        header.className = 'device-header';
        header.appendChild(headerLeft);
        header.appendChild(headerRight);
        
        // Create services container (initially hidden)
        const services = document.createElement('div');
        services.id = servicesId;
        services.className = 'device-services';
        
        // Create device row
        const row = document.createElement('div');
        row.className = `device ${isActive ? 'active' : 'not-active'}`;
        row.appendChild(header);
        row.appendChild(services);
        
        // Add click handler to toggle collapse (only on header, not on buttons)
        header.onclick = (e) => {
            // Don't toggle if clicking on a button or interactive element
            const target = e.target as HTMLElement;
            if (target.tagName === 'BUTTON' || target.closest('button') || target.closest('a') || target.closest('select')) {
                return;
            }
            row.classList.toggle('expanded');
            const button = row.querySelector(`#${collapseButtonId}`) as HTMLElement;
            if (button) {
                button.textContent = row.classList.contains('expanded') ? '▼' : '▶';
            }
        };
        
        // Also allow clicking directly on the collapse button
        collapseButton.onclick = (e) => {
            e.stopPropagation();
            row.classList.toggle('expanded');
            collapseButton.textContent = row.classList.contains('expanded') ? '▼' : '▶';
        };

        DeviceTracker.tools.forEach((tool) => {
            const entry = tool.createEntryForDeviceList(device, blockClass, this.params);
            if (entry) {
                if (Array.isArray(entry)) {
                    entry.forEach((item) => {
                        item && services.appendChild(item);
                    });
                } else {
                    services.appendChild(entry);
                }
            }
        });

        const streamEntry = StreamClientScrcpy.createEntryForDeviceList(device, blockClass, fullName, this.params);
        streamEntry && services.appendChild(streamEntry);

        DESC_COLUMNS.forEach((item) => {
            const { title } = item;
            const fieldName = item.field;
            let value: string;
            if (typeof item.field === 'string') {
                value = '' + device[item.field];
            } else {
                value = item.field(device);
            }
            const td = document.createElement('div');
            td.classList.add(DeviceTracker.titleToClassName(title), blockClass);
            services.appendChild(td);
            if (fieldName === 'pid') {
                hasPid = value !== '-1';
                const actionButton = document.createElement('button');
                actionButton.className = 'action-button kill-server-button';
                actionButton.setAttribute(Attribute.UDID, device.udid);
                actionButton.setAttribute(Attribute.PID, value);
                let command: string;
                if (isActive) {
                    actionButton.classList.add('active');
                    actionButton.onclick = this.onActionButtonClick;
                    if (hasPid) {
                        command = ControlCenterCommand.KILL_SERVER;
                        actionButton.title = 'Kill server';
                        actionButton.appendChild(SvgImage.create(SvgImage.Icon.CANCEL));
                    } else {
                        command = ControlCenterCommand.START_SERVER;
                        actionButton.title = 'Start server';
                        actionButton.appendChild(SvgImage.create(SvgImage.Icon.REFRESH));
                    }
                    actionButton.setAttribute(Attribute.COMMAND, command);
                } else {
                    const timestamp = device['last.update.timestamp'];
                    if (timestamp) {
                        const date = new Date(timestamp);
                        actionButton.title = `Last update on ${date.toLocaleDateString()} at ${date.toLocaleTimeString()}`;
                    } else {
                        actionButton.title = `Not active`;
                    }
                    actionButton.appendChild(SvgImage.create(SvgImage.Icon.OFFLINE));
                }
                const span = document.createElement('span');
                span.innerText = value;
                actionButton.appendChild(span);
                td.appendChild(actionButton);
            } else if (fieldName === 'interfaces') {
                const proxyInterfaceUrl = DeviceTracker.createUrl(this.params, device.udid).toString();
                const proxyInterfaceName = 'proxy';
                const localStorageKey = DeviceTracker.getLocalStorageKey(fullName);
                const lastSelected = localStorage && localStorage.getItem(localStorageKey);
                const selectElement = document.createElement('select');
                selectElement.setAttribute(Attribute.UDID, device.udid);
                selectElement.setAttribute(Attribute.FULL_NAME, fullName);
                selectElement.setAttribute(
                    'name',
                    encodeURIComponent(`${DeviceTracker.AttributePrefixInterfaceSelectFor}${fullName}`),
                );
                /// #if SCRCPY_LISTENS_ON_ALL_INTERFACES
                device.interfaces.forEach((value) => {
                    const params = {
                        ...this.params,
                        secure: false,
                        hostname: value.ipv4,
                        port: SERVER_PORT,
                    };
                    const url = DeviceTracker.createUrl(params).toString();
                    const optionElement = DeviceTracker.createInterfaceOption(value.name, url);
                    optionElement.innerText = `${value.name}: ${value.ipv4}`;
                    selectElement.appendChild(optionElement);
                    if (lastSelected) {
                        if (lastSelected === value.name || !selectedInterfaceName) {
                            optionElement.selected = true;
                            selectedInterfaceUrl = url;
                            selectedInterfaceName = value.name;
                        }
                    } else if (device['wifi.interface'] === value.name) {
                        optionElement.selected = true;
                    }
                });
                /// #else
                selectedInterfaceUrl = proxyInterfaceUrl;
                selectedInterfaceName = proxyInterfaceName;
                td.classList.add('hidden');
                /// #endif
                if (isActive) {
                    const adbProxyOption = DeviceTracker.createInterfaceOption(proxyInterfaceName, proxyInterfaceUrl);
                    if (lastSelected === proxyInterfaceName || !selectedInterfaceName) {
                        adbProxyOption.selected = true;
                        selectedInterfaceUrl = proxyInterfaceUrl;
                        selectedInterfaceName = proxyInterfaceName;
                    }
                    selectElement.appendChild(adbProxyOption);
                    const actionButton = document.createElement('button');
                    actionButton.className = 'action-button update-interfaces-button active';
                    actionButton.title = `Update information`;
                    actionButton.appendChild(SvgImage.create(SvgImage.Icon.REFRESH));
                    actionButton.setAttribute(Attribute.UDID, device.udid);
                    actionButton.setAttribute(Attribute.COMMAND, ControlCenterCommand.UPDATE_INTERFACES);
                    actionButton.onclick = this.onActionButtonClick;
                    td.appendChild(actionButton);
                }
                selectElement.onchange = this.onInterfaceSelected;
                td.appendChild(selectElement);
            } else {
                td.innerText = value;
            }
        });

        if (DeviceTracker.CREATE_DIRECT_LINKS) {
            const name = `${DeviceTracker.AttributePrefixPlayerFor}${fullName}`;
            StreamClientScrcpy.getPlayers().forEach((playerClass) => {
                const { playerCodeName, playerFullName } = playerClass;
                const playerTd = document.createElement('div');
                playerTd.classList.add(blockClass);
                playerTd.setAttribute('name', encodeURIComponent(name));
                playerTd.setAttribute(DeviceTracker.AttributePlayerFullName, encodeURIComponent(playerFullName));
                playerTd.setAttribute(DeviceTracker.AttributePlayerCodeName, encodeURIComponent(playerCodeName));
                services.appendChild(playerTd);
            });
        }

        tbody.appendChild(row);
        if (DeviceTracker.CREATE_DIRECT_LINKS && hasPid && selectedInterfaceUrl) {
            this.updateLink({
                url: selectedInterfaceUrl,
                name: selectedInterfaceName,
                fullName,
                udid: device.udid,
                store: false,
            });
        }
    }

    protected getChannelCode(): string {
        return ChannelCode.GTRC;
    }

    private buildDeviceIframes(): void {
        const iframesContainer = this.getOrCreateIframesContainer();
        
        // Clear existing iframes
        while (iframesContainer.firstChild) {
            iframesContainer.removeChild(iframesContainer.firstChild);
        }

        // Create iframes for each active device
        this.descriptors.forEach((device) => {
            if (device.state === DeviceState.DEVICE && device.pid !== -1) {
                const streamUrl = this.buildStreamUrl(device);
                if (streamUrl) {
                    const iframe = document.createElement('iframe');
                    iframe.src = streamUrl;
                    iframe.className = 'device-stream-iframe';
                    iframe.setAttribute('data-udid', device.udid);
                    iframe.setAttribute('frameborder', '0');
                    iframe.setAttribute('allowfullscreen', 'true');
                    iframesContainer.appendChild(iframe);
                }
            }
        });
    }

    private buildStreamUrl(device: GoogDeviceDescriptor): string | null {
        try {
            // Get the selected interface URL (same logic as in buildDeviceRow)
            const fullName = `${this.id}_${Util.escapeUdid(device.udid)}`;
            const proxyInterfaceUrl = DeviceTracker.createUrl(this.params, device.udid).toString();
            const proxyInterfaceName = 'proxy';
            const localStorageKey = DeviceTracker.getLocalStorageKey(fullName);
            const lastSelected = localStorage && localStorage.getItem(localStorageKey);
            
            let selectedInterfaceUrl = '';
            let selectedInterfaceName = '';
            
            // Check interfaces first (if SCRCPY_LISTENS_ON_ALL_INTERFACES is enabled)
            if (device.interfaces && device.interfaces.length > 0) {
                device.interfaces.forEach((value) => {
                    if (lastSelected) {
                        if (lastSelected === value.name || !selectedInterfaceName) {
                            const params = {
                                ...this.params,
                                secure: false,
                                hostname: value.ipv4,
                                port: SERVER_PORT,
                            };
                            selectedInterfaceUrl = DeviceTracker.createUrl(params).toString();
                            selectedInterfaceName = value.name;
                        }
                    } else if (device['wifi.interface'] === value.name && !selectedInterfaceName) {
                        const params = {
                            ...this.params,
                            secure: false,
                            hostname: value.ipv4,
                            port: SERVER_PORT,
                        };
                        selectedInterfaceUrl = DeviceTracker.createUrl(params).toString();
                        selectedInterfaceName = value.name;
                    }
                });
            }
            
            // If no interface selected yet, use proxy
            if (!selectedInterfaceUrl) {
                if (lastSelected === proxyInterfaceName || !selectedInterfaceName) {
                    selectedInterfaceUrl = proxyInterfaceUrl;
                    selectedInterfaceName = proxyInterfaceName;
                } else {
                    // Fallback to proxy if nothing else is available
                    selectedInterfaceUrl = proxyInterfaceUrl;
                }
            }

            if (!selectedInterfaceUrl) {
                return null;
            }

            // Build the stream URL
            const q: any = {
                action: ACTION.STREAM_SCRCPY,
                udid: device.udid,
                player: 'mse', // Default player
                ws: selectedInterfaceUrl,
            };

            let { hostname } = this.params;
            let port: string | number | undefined = this.params.port;
            let pathname = this.params.pathname ?? location.pathname;
            let protocol = this.params.secure ? 'https:' : 'http:';
            
            if (this.params.useProxy) {
                q.hostname = hostname;
                q.port = port;
                q.pathname = pathname;
                q.secure = this.params.secure;
                q.useProxy = true;
                protocol = location.protocol;
                hostname = location.hostname;
                port = location.port;
                pathname = location.pathname;
            }

            const hash = `#!${new URLSearchParams(q).toString()}`;
            return `${protocol}//${hostname}:${port}${pathname}${hash}`;
        } catch (error) {
            console.error('[DeviceTracker] Error building stream URL:', error);
            return null;
        }
    }

    private getOrCreateIframesContainer(): HTMLElement {
        const containerId = 'device-stream-iframes';
        let container = document.getElementById(containerId);
        if (!container) {
            container = document.createElement('div');
            container.id = containerId;
            container.className = 'device-stream-iframes-container';
            
            // Get or create the main layout container
            const layoutContainer = this.getOrCreateLayoutContainer();
            layoutContainer.appendChild(container);
        }
        return container;
    }

    private getOrCreateLayoutContainer(): HTMLElement {
        const layoutId = 'device-layout-container';
        let layoutContainer = document.getElementById(layoutId);
        if (!layoutContainer) {
            layoutContainer = document.createElement('div');
            layoutContainer.id = layoutId;
            layoutContainer.className = 'device-layout-container';
            
            // Move the devices container into the layout container if it exists
            const devicesContainer = document.getElementById(BaseDeviceTracker.HOLDER_ELEMENT_ID);
            if (devicesContainer) {
                const parent = devicesContainer.parentElement;
                if (parent) {
                    parent.removeChild(devicesContainer);
                }
                layoutContainer.appendChild(devicesContainer);
            }
            
            // Append layout container to body
            document.body.appendChild(layoutContainer);
        } else {
            // Layout container exists, but make sure devices container is inside it
            const devicesContainer = document.getElementById(BaseDeviceTracker.HOLDER_ELEMENT_ID);
            if (devicesContainer && devicesContainer.parentElement !== layoutContainer) {
                const parent = devicesContainer.parentElement;
                if (parent) {
                    parent.removeChild(devicesContainer);
                }
                layoutContainer.appendChild(devicesContainer);
            }
        }
        return layoutContainer;
    }

    public destroy(): void {
        super.destroy();
        DeviceTracker.instancesByUrl.delete(this.url.toString());
        if (!DeviceTracker.instancesByUrl.size) {
            const holder = document.getElementById(BaseDeviceTracker.HOLDER_ELEMENT_ID);
            if (holder && holder.parentElement) {
                holder.parentElement.removeChild(holder);
            }
            // Also remove iframes container if no trackers remain
            const iframesContainer = document.getElementById('device-stream-iframes');
            if (iframesContainer && iframesContainer.parentElement) {
                iframesContainer.parentElement.removeChild(iframesContainer);
            }
            // Remove layout container if no trackers remain
            const layoutContainer = document.getElementById('device-layout-container');
            if (layoutContainer && layoutContainer.parentElement) {
                layoutContainer.parentElement.removeChild(layoutContainer);
            }
        }
    }
}
